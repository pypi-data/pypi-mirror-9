# coding:utf8

"""
Created on 2014-07-17

@author: tufei
@description:
         
Copyright (c) 2014 infohold inc. All rights reserved.
"""
import functools
import random
import datetime
import types
from dhkit import log
from error import Error
from google.protobuf.message import DecodeError
from google.protobuf.service import RpcController, RpcChannel, RpcException
import zmq
import errno
import threading
import rpc_pb2


def interrupt_wrap(func, *args, **kwargs):
    while True:
        try:
            return func(*args, **kwargs)
        except zmq.ZMQError as e:
            # interrupted, try again
            if e.errno == errno.EINTR:
                continue
            else:
                # real error, raise it
                raise e


class LogicException(RpcException):

    def __init__(self, code, msg):
        self.code = code
        self.msg = msg

    def __str__(self):
        return "code:[%s] msg:[%s]" % (self.code, self.msg)


class ZMQRpcController(RpcController):

    def __init__(self):
        self.cancel = False
        self.error_text = None
        self.callback = None

    def Reset(self):
        self.cancel = False
        self.error_text = None
        self.callback = None

    def Failed(self):
        return True if self.error_text is not None else False

    def ErrorText(self):
        return self.error_text

    def StartCancel(self):
        self.cancel = True
        if self.callback is not None:
            self.callback()

    def SetFailed(self, reason):
        self.error_text = reason

    def IsCanceled(self):
        return self.cancel

    def NotifyOnCancel(self, callback):
        self.callback = callback


class ZMQRpcChannel(RpcChannel):

    def __init__(self, binding=None, timeout=None, context=None):
        self.binding = binding or "tcp://127.0.0.1:9088"
        self.timeout = timeout or 10000
        self.context = context or zmq.Context.instance(io_threads=1)
        self.socket = self.context.socket(zmq.REQ)

    def _connect(self):
        #self.socket.setsockopt(zmq.IDENTITY, self.identity)
        self.socket.setsockopt(zmq.LINGER, 0)
        self.socket.connect(self.binding)

    def _close(self):
        try:
            self.socket.close()
        except zmq.ZMQBaseError:
            log.exception("close socket error.")
            pass

    def _generate_msgid(self):
        rand = random.randint(1000, 9999)
        return "%s%d" % (datetime.datetime.now().strftime("%Y%m%d%H%M%S%f"), rand)

    def _generate_req_message(self, method_descriptor, request):
        rpc_req = rpc_pb2.RpcRequest()
        rpc_req.method = method_descriptor.full_name
        rpc_req.msgid = self._generate_msgid()
        rpc_req.protobuf = request.SerializeToString()
        return rpc_req

    def CallMethod(self, method_descriptor, rpc_controller, request, response_class, done):
        try:
            self._connect()

            poll = zmq.Poller()
            poll.register(self.socket, zmq.POLLIN)

            rpc_req = self._generate_req_message(method_descriptor, request)
            self.socket.send(rpc_req.SerializeToString())

            sockets = dict(poll.poll(self.timeout))
            if self.socket in sockets and sockets[self.socket] == zmq.POLLIN:
                proto_resp = self.socket.recv()
                rpc_resp = rpc_pb2.RpcResponse()
                rpc_resp.ParseFromString(proto_resp)
                if rpc_resp.return_code != 0:
                    raise LogicException(rpc_resp.return_code, rpc_resp.return_message)

                response = response_class()
                response.ParseFromString(rpc_resp.protobuf)
                return response
            else:
                raise RpcException("Request ZMQ Server: %s timeout" % self.binding)
        finally:
            self._close()


class ZMQRpcServer(object):

    def __init__(self, binding=None, worker_num=16):
        self.binding = binding or "tcp://*:9088"
        self.context = zmq.Context(io_threads=1)
        self.running = True

        self.worker_num = worker_num
        self.server_thread = None
        self.worker_threads = []

        self.service_map = dict()

    def register_service(self, service):
        methods = service.GetDescriptor().methods
        for method in methods:
            self.service_map[method.full_name] = service

    def start(self):
        self.server_thread = threading.Thread(target=self.server_routine)
        self.server_thread.start()
        log.debug('zmq rpc server thread started.')

        for i in xrange(self.worker_num):
            worker = threading.Thread(target=self.worker_routine)
            self.worker_threads.append(worker)
            worker.start()
            log.debug('zmq rpc worker thread started.')

    def stop(self):
        self.running = False
        self.context.term()

    def join(self):
        self.server_thread.join()

    def server_routine(self):
        frontend = self.context.socket(zmq.ROUTER)
        frontend.bind(self.binding)

        backend = self.context.socket(zmq.DEALER)
        backend.bind("inproc://backend")

        poll = zmq.Poller()
        poll.register(frontend, zmq.POLLIN)
        poll.register(backend, zmq.POLLIN)

        while self.running:
            try:
                sockets = dict(interrupt_wrap(poll.poll))
                if frontend in sockets and sockets[frontend] == zmq.POLLIN:
                    msg_parts = interrupt_wrap(frontend.recv_multipart)
                    interrupt_wrap(backend.send_multipart, msg_parts)
                if backend in sockets and sockets[backend] == zmq.POLLIN:
                    msg_parts = interrupt_wrap(backend.recv_multipart)
                    interrupt_wrap(frontend.send_multipart, msg_parts)
            except zmq.ContextTerminated:
                log.exception("ZMQ Server Context terminated.")
                break

    def worker_routine(self):
        worker = self.context.socket(zmq.REP)
        worker.connect("inproc://backend")
        while self.running:
            try:
                msg_req = interrupt_wrap(worker.recv)
                rpc_req = rpc_pb2.RpcRequest()
                rpc_req.ParseFromString(msg_req)
                log.debug("Receive rpc request ok. method:[%s] msgid:[%s]" % (rpc_req.method, rpc_req.msgid))
                rpc_response = self.handle_message(rpc_req)
                interrupt_wrap(worker.send, rpc_response.SerializeToString())
                log.debug("Send rpc reponse ok. method:[%s] msgid:[%s]" % (rpc_response.method, rpc_response.msgid))
            except DecodeError:
                log.warning("unknown protobuf rpc message.")
                continue
            except zmq.ContextTerminated:
                log.exception("zmq context terminated.")
                break
            except Exception:
                log.exception("handle worker error.")
                import traceback
                traceback.print_exc()
                break

        worker.close()

    def handle_message(self, rpc_req):
        rpc_response = rpc_pb2.RpcResponse()
        rpc_response.method = rpc_req.method
        rpc_response.msgid = rpc_req.msgid
        rpc_response.return_code = 0
        rpc_response.return_message = 'success'

        controller = ZMQRpcController()
        service = self.service_map.get(rpc_req.method)
        if service is None:
            controller.SetFailed("request method:%s not found" % rpc_req.method)
            log.debug(controller.ErrorText())
            rpc_response.return_code = -200
            rpc_response.return_message = controller.ErrorText()
            return rpc_response

        try:
            method = service.GetDescriptor().FindMethodByName(self._get_last_name(rpc_req.method))
            request = service.GetRequestClass(method)()
            request.ParseFromString(rpc_req.protobuf)
            response = service.CallMethod(method, controller, request, None)
            rpc_response.protobuf = response.SerializeToString()
        except Error, e:
            log.exception("handle method: %s error" % rpc_req.method)
            controller.SetFailed("service return error: %s" % e.desc)
            rpc_response.return_code = e.code
            rpc_response.return_message = e.desc
        except Exception, e:
            log.exception("handle method: %s internal error" % rpc_req.method)
            controller.SetFailed("server internal error: %s" % e.message)
            rpc_response.return_code = -100
            rpc_response.return_message = controller.ErrorText()

        return rpc_response

    def _get_last_name(self, method_name):
        if method_name is None:
            return method_name
        lst = method_name.split(".")
        if len(lst) == 1:
            return method_name
        else:
            return lst[-1]


def service_method(func):
    """Protobuf RPC服务实现方法装饰器。

    目前暂时不会用到rpc_controler和callback
    :param func:
    :return:
    """
    @functools.wraps(func)
    def _wrapper(self, rpc_controler, request, callback):
        return func(self, request)
    return _wrapper

