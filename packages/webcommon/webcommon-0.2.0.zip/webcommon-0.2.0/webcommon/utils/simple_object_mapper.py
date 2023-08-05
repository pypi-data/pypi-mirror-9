# Copyright (C) 2015, Availab.io(R) Ltd. All rights reserved.


class SimpleObjectMapper:
    """
    Base class for mapping class attributes from one class to another one
    Supports mapping conversions too
    """

    def __init__(self, to_type, mappings=None):
        """Constructor

        Args:
            to_type: type of the target object
            mappings: dictionary of the attribute conversions


        Attributes:
            to_type: type of the target object
            mappings: dictionary of the attribute conversions

        Examples:

            1. Mapping of the properties without mapping definition
            In this case are mapped only these properties of the target class which
            are in target and source classes. Other properties are not mapped.
            Suppose we have class 'A' with attributes 'name' and 'last_name'
            and class 'B' with attribute 'name'.
            Initialization of the ObjectMapper will be:
            mapper = SimpleObjectMapper(B)
            instance_b = mapper.map(A())

            In this case, value of A.name will be copied into B.name.

            2. Mapping with defined mapping functions
            Suppose we have class 'A' with attributes 'first_name' and 'last_name'
            and class 'B' with attribute 'name' and want to map it in a way
            'B.name' = 'A.first_name' + 'A.last_name'
            Initialization of the SimpleObjectMapper will be:
            mapper = SimpleObjectMapper(B, {name: lambda a : a.first_name + " " + a.last_name})
            instance_b = mapper.map(A())

            In this case, to the B.name will be mapped A.first_name + " " + A.last_name

            3. Mapping suppression
            For some purposes, it can be needed to suppress some mapping.
            Suppose we have class 'A' with attributes 'name' and 'last_name'
            and class 'B' with attributes 'name' and 'last_name'.
            And we want to map only the A.name into B.name, but not A.last_name to
            b.last_name
            Initialization of the SimpleObjectMapper will be:
            mapper = SimpleObjectMapper(B,, {'last_name': None})
            instance_b = mapper.map(A())

            In this case, value of A.name will be copied into B.name automatically by the attribute name 'name'.
            Attribute A.last_name will be not mapped thanks the suppression (lambda function is None).


        Returns:
          Instance of the ObjectMapper
        """
        self.to_type = to_type
        self.mappings = mappings
        pass

    def map(self, from_obj):
        """Method for creating target object instance

        Args:
          from_obj: source object to be mapped from
          mappings: dictionary of the attribute conversions

        Returns:
          Instance of the target class with mapped attributes
        """
        inst = self.to_type()
        from_props = from_obj.__dict__
        to_props = inst.__dict__

        for prop in to_props:
            if self.mappings is not None and prop in self.mappings:
                # mapping function for the property found
                try:
                    fnc = self.mappings[prop]
                    if fnc is not None:
                        setattr(inst, prop, fnc(from_obj))
                        # none suppress mapping
                except Exception:
                    raise Exception("Invalid mapping while setting property {0}.{1}". \
                                    format(inst.__class__.__name__, prop))

            else:
                # try find property with the same name
                if prop in from_props:
                    setattr(inst, prop, from_props[prop])
                    # case when target property is not mapped (can be extended)

        return inst