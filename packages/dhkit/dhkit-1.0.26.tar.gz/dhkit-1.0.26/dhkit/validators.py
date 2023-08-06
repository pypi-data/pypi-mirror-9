#coding:utf8

"""
Created on 2013-7-23

@author: tufei
@description:
         
Copyright (c) 2013 infohold inc. All rights reserved.
"""
import re


EMPTY_VALUES = (None, '', [], (), {})


class ValidationError(Exception):
    pass


class Validator(object):

    def __init__(self, limit_value=None):
        self.limit_value = limit_value

    def _check_valid(self, value):
        return False

    def _clean(self, value):
        return value

    def _get_error_message(self, value):
        return "validation error"

    def __call__(self, value):
        if not self._check_valid(self._clean(value)):
            msg = self._get_error_message(value)
            raise ValidationError(msg)


class EmptyValidator(Validator):
    """空验证器，总是验证成功
    """

    def _check_valid(self, value):
        return True


class IntegerValidator(Validator):

    def _check_valid(self, value):
        try:
            int(value)
            return True
        except ValueError:
            return False

    def _get_error_message(self, value):
        return "值: [%s] 不是一个有效的整型类型" % value


class FloatValidator(Validator):

    def _check_valid(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def _get_error_message(self, value):
        return "值: [%s] 不是一个有效的浮点类型" % value


class MaxValueValidator(Validator):

    def _check_valid(self, value):
        typ = type(self.limit_value)
        if not isinstance(value, typ):
            raise ValidationError("value type must be %s" % typ)
        return value <= self.limit_value

    def _get_error_message(self, value):
        return "值: [%s] 超过了最大值: %s" % (value, self.limit_value)


class MinValueValidator(Validator):

    def _check_valid(self, value):
        typ = type(self.limit_value)
        if not isinstance(value, typ):
            raise ValidationError("value type must be %s" % typ)
        return value >= self.limit_value

    def _get_error_message(self, value):
        return "值: [%s] 小于最小值: %s" % (value, self.limit_value)


class MinLengthValidator(Validator):

    def _check_valid(self, value):
        return value >= self.limit_value

    def _clean(self, value):
        return len(value)

    def _get_error_message(self, value):
        return "值长度: [%s] 小于最小长度范围: %s" % (value, self.limit_value)


class MaxLengthValidator(Validator):

    def _check_valid(self, value):
        return value <= self.limit_value

    def _clean(self, value):
        return len(value)

    def _get_error_message(self, value):
        return "值长度: [%s] 超过最大长度范围: %s" % (value, self.limit_value)


class AcceptValidator(Validator):

    def _check_valid(self, value):
        return value in self.limit_value

    def _get_error_message(self, value):
        return "值: [%s] 不在可接受的集合范围内: %s" % (value, self.limit_value)


class RegexValidator(Validator):
    regex = None

    def _check_valid(self, value):
        return self.regex.search(value)

    def _clean(self, value):
        return str(value)


class EmailValidator(RegexValidator):
    regex = re.compile(
        r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"
        r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"'
        r')@((?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)$)'
        r'|\[(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}\]$', re.IGNORECASE)

    def _get_error_message(self, value):
        return "[%s] 不是一个有效的邮箱号" % value


class PhoneValidator(RegexValidator):
    regex = re.compile(r"^(1(([35][0-9])|(47)|(97)|[8][0-9]))\d{8}$")

    def _get_error_message(self, value):
        return "[%s] 不是一个有效的手机号码" % value


class DateValidator(RegexValidator):
    """校验标准的YYYY-MM-DD日期格式
    """
    regex = re.compile(r"^((((19|20)\d{2})-(0?(1|[3-9])|1[012])-(0?[1-9]|[12]\d|30))"
                       r"|(((19|20)\d{2})-(0?[13578]|1[02])-31)|(((19|20)\d{2})-0?2-(0?[1-9]|1\d|2[0-8]))"
                       r"|((((19|20)([13579][26]|[2468][048]|0[48]))|(2000))-0?2-29))$")

    def _get_error_message(self, value):
        return "[%s] 不是一个有效的日期格式" % value


class IPV4AddressValidator(RegexValidator):
    regex = re.compile(r'^(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}$')


class IDValidator(Validator):

    def _check_valid(self, value):
        cleaned_value = self._clean(value)
        iW = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2, 1]  # 权重数组
        values = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'x'] # 身份证号码中可能的字符

        r = re.compile('^[1-9][0-9]{16}[x0-9]$', re.IGNORECASE)
        m = r.match(cleaned_value)
        if not m:
            return False

        s = 0
        for i in range(0,17):
            s += int(cleaned_value[i]) * iW[i]
        chk_val = (12 - (s % 11)) % 11
        return cleaned_value[17].lower() == values[chk_val]

    def _get_error_message(self, value):
        return "[%s] 不是一个有效的证件号" % value

    def _clean(self, value):
        return str(value)


class IPV6AddressValidator(Validator):

    def _check_valid(self, value):
        # We need to have at least one ':'.
        if ':' not in value:
            return False

        # We can only have one '::' shortener.
        if value.count('::') > 1:
            return False

        # '::' should be encompassed by start, digits or end.
        if ':::' in value:
            return False

        # A single colon can neither start nor end an address.
        if ((value.startswith(':') and not value.startswith('::')) or
                (value.endswith(':') and not value.endswith('::'))):
            return False

        # We can never have more than 7 ':' (1::2:3:4:5:6:7:8 is invalid)
        if value.count(':') > 7:
            return False

        # If we have no concatenation, we need to have 8 fields with 7 ':'.
        if '::' not in value and value.count(':') != 7:
            # We might have an IPv4 mapped address.
            if value.count('.') != 3:
                return False

        ip_str = self._explode_shorthand_ip_string(value)

        # Now that we have that all squared away, let's check that each of the
        # hextets are between 0x0 and 0xFFFF.
        for hextet in ip_str.split(':'):
            if hextet.count('.') == 3:
                # If we have an IPv4 mapped address, the IPv4 portion has to
                # be at the end of the IPv6 portion.
                if not ip_str.split(':')[-1] == hextet:
                    return False
                try:
                    self._validate_ipv4_address(hextet)
                except ValidationError:
                    return False
            else:
                try:
                    # a value error here means that we got a bad hextet,
                    # something like 0xzzzz
                    if int(hextet, 16) < 0x0 or int(hextet, 16) > 0xFFFF:
                        return False
                except ValueError:
                    return False
        return True

    def _clean(self, value):
        return str(value)

    def _validate_ipv4_address(self, ipv4_str):
        validate_ipv4_address =  IPV4AddressValidator()
        return validate_ipv4_address(ipv4_str)

    def _explode_shorthand_ip_string(self, ip_str):
        """
        Expand a shortened IPv6 address.

        Args:
            ip_str: A string, the IPv6 address.

        Returns:
            A string, the expanded IPv6 address.

        """
        if not self._is_shorthand_ip(ip_str):
            # We've already got a longhand ip_str.
            return ip_str

        new_ip = []
        hextet = ip_str.split('::')

        # If there is a ::, we need to expand it with zeroes
        # to get to 8 hextets - unless there is a dot in the last hextet,
        # meaning we're doing v4-mapping
        if '.' in ip_str.split(':')[-1]:
            fill_to = 7
        else:
            fill_to = 8

        if len(hextet) > 1:
            sep = len(hextet[0].split(':')) + len(hextet[1].split(':'))
            new_ip = hextet[0].split(':')

            for _ in xrange(fill_to - sep):
                new_ip.append('0000')
            new_ip += hextet[1].split(':')

        else:
            new_ip = ip_str.split(':')

        # Now need to make sure every hextet is 4 lower case characters.
        # If a hextet is < 4 characters, we've got missing leading 0's.
        ret_ip = []
        for hextet in new_ip:
            ret_ip.append(('0' * (4 - len(hextet)) + hextet).lower())
        return ':'.join(ret_ip)

    def _is_shorthand_ip(self, ip_str):
        """Determine if the address is shortened.

        Args:
            ip_str: A string, the IPv6 address.

        Returns:
            A boolean, True if the address is shortened.

        """
        if ip_str.count('::') == 1:
            return True
        if any(len(x) < 4 for x in ip_str.split(':')):
            return True
        return False

if __name__ == '__main__':
    v = IPV4AddressValidator()
    v2 = EmailValidator()
    #v('192.168.0.361')
    v2("2@com")