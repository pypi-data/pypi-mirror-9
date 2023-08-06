from json import JSONDecoder

__decoder = JSONDecoder()

possible_json_values = object, tuple, (tuple, object)
possible_other_values = str, tuple, None


def jsonfinder(s, json=object, other=None, decoder=None):
    if json not in possible_json_values or other not in possible_other_values:
        raise TypeError
    decoder = decoder or __decoder
    string_start = find_start = 0
    while 1:
        json_start = s.find('{', find_start)
        if json_start == -1:
            if other is tuple:
                yield string_start, len(s)
            elif other is str:
                yield s[string_start:len(s)]
            return
        try:
            obj, end = decoder.raw_decode(s, idx=json_start)
        except ValueError:
            find_start = json_start + 1
        else:
            if other is tuple:
                yield string_start, json_start
            elif other is str:
                yield s[string_start:json_start]

            if json is object:
                yield obj
            elif json is tuple:
                yield json_start, end
            else:
                yield (json_start, end), obj

            string_start = find_start = end

__all__ = ["jsonfinder"]