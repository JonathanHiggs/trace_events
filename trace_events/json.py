from json import JSONDecoder, JSONEncoder

from .events import Trace, ALL_EVENT_TYPES


class TraceJsonEncoder(JSONEncoder):
    """
    Converts trace objects to json representations
    """

    def default(self, obj):
        if hasattr(obj, 'to_json') and callable(obj.to_json):
            return obj.to_json()

        if isinstance(obj, Trace):
            return dict(
                traceEvents=obj.trace_events,
                otherData=obj.other_data)

        return super().default(obj)


class TraceJsonDecoder(JSONDecoder):
    def __init__(self, *args, **kwargs):
        JSONDecoder.__init__(
            self, object_hook=TraceJsonDecoder.object_hook, *args, **kwargs)

    @staticmethod
    def object_hook(data: dict):
        if Trace.trace_events_field.name in data:
            return Trace.from_dict(data)

        if 'ph' in data:
            event_type = data.get('ph')
            assert isinstance(
                event_type, str), f'event_type value is {type(event_type).__name__} should be a str'

            event_type = next(
                (t for t in ALL_EVENT_TYPES if event_type == t.event_type), None)
            if event_type is None:
                raise TypeError(
                    f'Unable to process event with \'ph\': \'{event_type}\'')
            return event_type.from_dict(data)

        return data
