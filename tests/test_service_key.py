from pyfunq.service_key import ServiceKey


class TestServiceKey:
    def test_keys_equal_by_service_type_and_factory_type(self):
        dict_value: dict[str, str] = {}
        dict_type = type(dict_value)
        service_key1 = ServiceKey(dict_type, tuple([dict_type]))
        service_key2 = ServiceKey(dict_type, tuple([dict_type]))

        assert service_key1 == service_key2
        assert service_key1.__hash__() == service_key2.__hash__()

    def test_keys_should_not_be_equal_given_different_service_type(self):
        set_value: set[str] = set()
        set_type = type(set_value)
        dict_value: dict[str, str] = {}
        dict_type = type(dict_value)
        service_key1 = ServiceKey(set_type, tuple([dict_type]))
        service_key2 = ServiceKey(dict_type, tuple([dict_type]))

        assert service_key1 != service_key2
        assert service_key1.__hash__() != service_key2.__hash__()

    def test_keys_should_not_be_equal_given_different_factory_type(self):
        set_value: set[str] = set()
        set_type = type(set_value)
        dict_value: dict[str, str] = {}
        dict_type = type(dict_value)
        service_key1 = ServiceKey(set_type, tuple([set_type]))
        service_key2 = ServiceKey(dict_type, tuple([dict_type]))

        assert service_key1 != service_key2
        assert service_key1.__hash__() != service_key2.__hash__()

    def test_named_keys_should_be_equal_given_the_same__name(self):
        set_value: set[str] = set()
        set_type = type(set_value)
        dict_value: dict[str, str] = {}
        dict_type = type(dict_value)
        name = "tests"
        service_key1 = ServiceKey(set_type, tuple([set_type]), name)
        service_key2 = ServiceKey(dict_type, tuple([dict_type]), name)

        assert service_key1 != service_key2
        assert service_key1.__hash__() != service_key2.__hash__()

    def test_named_keys_should_not_be_equal_given_different_name(self):
        set_value: set[str] = set()
        set_type = type(set_value)
        dict_value: dict[str, str] = {}
        dict_type = type(dict_value)
        service_key1 = ServiceKey(set_type, tuple([set_type]), "name1")
        service_key2 = ServiceKey(dict_type, tuple([dict_type]), "name2")

        assert service_key1 != service_key2
        assert service_key1.__hash__() != service_key2.__hash__()
