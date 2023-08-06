# coding: utf-8
from functools import wraps


class Permission(object):
    def __init__(self):
        rule = self.rule()
        if not rule:
            raise AttributeError()
        self.rule = rule

    def __call__(self, func):
        """Give Permission instance the ability to be used as view decorator."""

        @wraps(func)
        def decorator(*args, **kwargs):
            if not self.check():
                return self.deny()
            return func(*args, **kwargs)

        return decorator

    def rule(self):
        """Add rule to this permission.

        Must be overrided."""
        raise NotImplementedError

    def check(self):
        """Check rule."""
        result, self.deny = self.rule.run()
        return result

    def show(self):
        """Show the structure of rule, only for debug."""
        self.rule.show()


class Rule(object):
    def __init__(self):
        self.rules_list = [[(self.check, self.deny)]]
        # if subclass override base(), serial merge the return rule's
        # rules_list to self.rules_list.
        base_rule = self.base()
        if base_rule:
            self.rules_list = Rule._and(base_rule.rules_list, self.rules_list)

    def __and__(self, other):
        """& bitwise operation.

        Serial merge self.rules_list to other.rules_list and return self.
        """
        self.rules_list = Rule._and(self.rules_list, other.rules_list)
        return self

    def __or__(self, other):
        """| bitwise operation.

        Parallel merge self.rules_list to other.rules_list and return self.
        """
        for rule in other.rules_list:
            self.rules_list.append(rule)
        return self

    def show(self):
        """Show the structure of self.rules_list, only for debug."""
        for rule in self.rules_list:
            result = ", ".join([str(check) for check, deny in rule])
            print(result)

    def base(self):
        """Add base rule."""
        return None

    def run(self):
        """Run self.rules_list.

        Return True if one rule channel has been passed.
        Otherwise return False and the deny() method of the last failed rule.
        """
        failed_result = None
        for rule in self.rules_list:
            for check, deny in rule:
                if not check():
                    failed_result = (False, deny)
                    break
            else:
                return (True, None)
        return failed_result

    def check(self):
        """Codes to determine whether this rule is passed.

        Must be overrided.
        """
        raise NotImplementedError()

    def deny(self):
        """Codes to be execute when check() failed.

        Must be overrided.
        """
        raise NotImplementedError()

    @staticmethod
    def _and(rules_list_pre, rules_list_pro):
        """Serial merge rule_list_pre to rule_list_pro."""
        return [rule_pre + rule_pro
                for rule_pre in rules_list_pre
                for rule_pro in rules_list_pro]
