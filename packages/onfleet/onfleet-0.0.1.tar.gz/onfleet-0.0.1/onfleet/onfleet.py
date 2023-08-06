import json
import requests

ONFLEET_API_ENDPOINT = "https://onfleet.com/api/v2/"
ONFLEET_ORGANIZATION_ID = "O1o6D8OrDDMILx2YEW3YOFFg"


class Organization(object):
    def __init__(self, id=None, created_on=None, updated_on=None, name=None, email=None, timezone=None, country=None, delegatee_ids=None, image=None):
        self.id = id
        self.created_on = created_on
        self.updated_on = updated_on
        self.name = name
        self.email = email
        self.timezone = timezone
        self.country = country
        self.delegatee_ids = delegatee_ids
        self.image = image

    def __repr__(self):
        return "<Organization id='{}'>".format(self.id)

    @classmethod
    def parse(self, obj):
        return Organization(
            id=obj['id'],
            created_on=obj['timeCreated'],
            updated_on=obj['timeLastModified'],
            name=obj['name'],
            email=obj['email'],
            delegatee_ids=obj['delegatees'],
            image=obj['image'],
            country=obj['country']
        )


class Administrator(object):
    def __init__(self, name, email, phone=None, id=None, user_type=None, organization_id=None, active=None, created_on=None, updated_on=None):
        self.name = name
        self.email = email
        self.phone = phone
        self.id = id
        self.user_type = user_type
        self.organization_id = organization_id
        self.active = active
        self.created_on = created_on
        self.updated_on = updated_on

    def __repr__(self):
        return "<Administrator id='{}'>".format(self.id)

    @classmethod
    def parse(self, obj):
        admin = Administrator(
            name=obj['name'],
            email=obj['email'],
            id=obj['id'],
            created_on=obj['timeCreated'],
            updated_on=obj['timeLastModified'],
            active=obj['isActive'],
            user_type=obj['type'],
            organization_id=obj['organization'],
        )

        admin.phone = obj.get('phone')
        return admin


class Recipient(object):
    def __init__(self, name, phone, notes=None, created_on=None, updated_on=None, id=None):
        self.id = id
        self.name = name
        self.phone = phone
        self.notes = notes
        self.created_on = created_on
        self.updated_on = updated_on

    def __repr__(self):
        return "<Recipient id='{}'>".format(self.id)

    @classmethod
    def parse(self, obj):
        recipient = Recipient(
            id=obj['id'],
            created_on=obj['timeCreated'],
            updated_on=obj['timeLastModified'],
            name=obj['name'],
            phone=obj['phone'],
            notes=obj['notes']
        )

        return recipient


class Task(object):
    UNASSIGNED = 0
    ASSIGNED = 1
    ACTIVE = 2
    COMPLETED = 3

    def __init__(self, destination, recipients, notes=None, state=None, id=None, created_on=None, updated_on=None, merchant=None, executor=None):
        self.id = id
        self.created_on = created_on
        self.updated_on = updated_on
        self.merchant = merchant
        self.executor = executor
        self.destination = destination
        self.recipients = recipients
        self.notes = notes

    def __repr__(self):
        return "<Task id='{}'>".format(self.id)

    @classmethod
    def parse(self, obj):
        task = Task(
            id=obj['id'],
            created_on=obj['timeCreated'],
            updated_on=obj['timeLastModified'],
            state=obj['state'],
            notes=obj['notes'],
            destination=Destination.parse(obj['destination']),
            recipients=map(Recipient.parse, obj['recipients'])
        )

        if 'worker' in obj and obj['worker'] is not None:
            task.worker = Worker.parse(obj['worker'])

        return task


class Address(object):
    def __init__(self, street=None, number=None, city=None, country=None, name=None, apartment=None, state=None, postal_code=None, unparsed=None):
        self.street = street
        self.number = number
        self.city = city
        self.country = country
        self.name = name
        self.apartment = apartment
        self.state = state
        self.postal_code = postal_code
        self.unparsed = unparsed

    def __repr__(self):
        return "<Address street='{}'>".format(self.street)

    @classmethod
    def parse(self, obj):
        address = Address(
            apartment=obj['apartment'],
            state=obj['state'],
            postal_code=obj['postalCode'],
            country=obj['country'],
            city=obj['city'],
            street=obj['street'],
            number=obj['number']
        )
        return address


class Destination(object):
    def __init__(self, address=None, location=None, notes=None, id=None, created_on=None, updated_on=None, tasks=None):
        self.id = id
        self.address = address
        self.location = location
        self.notes = notes

    def __repr__(self):
        return "<Destination id='{}'>".format(self.id)

    @classmethod
    def parse(self, obj):
        destination = Destination(
            id=obj['id'],
            created_on=obj['timeCreated'],
            updated_on=obj['timeLastModified'],
            location=obj['location'],
            address=Address.parse(obj['address']),
            notes=obj['notes'],
        )

        if 'tasks' in obj:
            destination.tasks = obj['tasks']

        return destination


class Vehicle(object):
    CAR = "CAR"
    MOTORCYCLE = "MOTORCYCLE"
    BICYCLE = "BICYCLE"
    TRUCK = "TRUCK"


    def __init__(self, vehicle_type, description=None, license_plate=None, color=None, id=None):
        if vehicle_type not in [Vehicle.CAR, Vehicle.MOTORCYCLE, Vehicle.BICYCLE, Vehicle.TRUCK]:
            raise Exception

        self.id = id
        self.vehicle_type = vehicle_type
        self.description = description
        self.license_plate = license_plate
        self.color = color

    def __repr__(self):
        return "<Vehicle id='{}'>".format(self.id)

    @classmethod
    def parse(self, obj):
        vehicle = Vehicle(
            id=obj['id'],
            vehicle_type=obj['type'],
        )

        if 'description' in obj:
            vehicle.team_ids = obj['description']

        if 'license_plate' in obj:
            vehicle.team_ids = obj['licensePlate']

        if 'color' in obj:
            vehicle.team_ids = obj['color']

        return vehicle


class Worker(object):
    def __init__(self, name=None, phone=None, team_ids=None, vehicle=None, id=None, tasks=None):
        self.id = id
        self.name = name
        self.phone = phone
        self.team_ids = team_ids
        self.vehicle = vehicle
        self.tasks = tasks

    def __repr__(self):
        return "<Worker name='{}'>".format(self.name)

    @classmethod
    def parse(self, obj):
        worker = Worker(
            id=obj['id'],
            name=obj['name'],
            phone=obj['phone'],
            vehicle=Vehicle.parse(obj['vehicle'])
        )

        if 'teams' in obj:
            worker.team_ids = obj['teams']

        return worker


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        payload = None

        if isinstance(obj, Administrator):
            payload = {
                'name': obj.name,
                'email': obj.email
            }

            optional_properties = {
                'phone': 'phone',
            }
        elif isinstance(obj, Vehicle):
            payload = {'type': obj.vehicle_type}

            optional_properties = {
                'description': 'description',
                'license_plate': 'licensePlate',
                'color': 'color'
            }
        elif isinstance(obj, Worker):
            payload = {
            }

            optional_properties = {
                'vehicle': 'vehicle',
                'tasks': 'tasks',
                'name': 'name',
                'phone': 'phone',
                'teams': 'team_ids'
            }
        elif isinstance(obj, Address):
            payload = {
            }

            optional_properties = {
                'street': 'street',
                'number': 'number',
                'city': 'city',
                'country': 'country',
                'name': 'name',
                'apartment': 'apartment',
                'state': 'state',
                'postal_code': 'postalCode',
                'unparsed': 'unparsed',
            }
        elif isinstance(obj, Destination):
            payload = {
            }

            optional_properties = {
                'address': 'address',
                'location': 'location',
                'notes': 'notes',
            }
        elif isinstance(obj, Task):
            payload = {
                'merchant': obj.merchant,
                'executor': obj.executor,
                'destination': obj.destination,
                'recipients': obj.recipients,
                'notes': obj.notes,
            }

            optional_properties = {}
        elif isinstance(obj, Recipient):
            payload = {
                'name': obj.name,
                'phone': obj.phone,
                'notes': obj.notes,
            }

            optional_properties = {}
        elif isinstance(obj, Administrator):
            payload = {
                'name': obj.name,
                'email': obj.email,
            }

            optional_properties = {'phone': obj.phone}

        if payload is None:
            return json.JSONEncoder.default(self, obj)
        else:
            for key, value in optional_properties.iteritems():
                if hasattr(obj, key) and getattr(obj, key) is not None:
                    payload[value] = getattr(obj, key)

            return payload


class Onfleet(object):
    def __init__(self, api_key):
        self.api_key = api_key

    def __getattr__(self, k):
        return OnfleetCall(self.api_key, k)


class OnfleetCall(object):
    def __init__(self, api_key, path):
        self.api_key = api_key
        self.components = [path]

    def __getattr__(self, k):
        self.components.append(k)
        return self

    def __getitem__(self, k):
        self.components.append(k)
        return self

    def __call__(self, *args, **kwargs):
        url = "{}{}".format(ONFLEET_API_ENDPOINT, "/".join(self.components))
        if 'method' in kwargs:
            method = kwargs['method']
            del kwargs['method']
        else:
            method = "GET"

        parse_response = kwargs.get('parse_response', True)

        if 'parse_response' in kwargs:
            del kwargs['parse_response']

        fun = getattr(requests, method.lower())
        if len(args) > 0:
            data = ComplexEncoder().encode(args[0])
        else:
            data = None

        response = fun(url, data=data, params=kwargs, auth=(self.api_key, ''), verify=False)

        parse_dictionary = {
            'workers': Worker,
            'tasks': Task,
            'recipients': Recipient,
            'destinations': Destination,
            'organization': Organization,
            'admins': Administrator
        }

        parse_as = None
        for component, parser in parse_dictionary.iteritems():
            if component in self.components:
                parse_as = parser

        json_response = response.json()

        if 'code' in json_response:
            message = json_response['message']

            if 'cause' in message:
                cause = message['cause']
                if cause['type'] == 'duplicateKey':
                    raise OnfleetDuplicateKeyException("{}: {} (value: '{}', key: '{}')" \
                            .format(message['error'], message['message'], cause['value'], cause['key']))

        if parse_response and parse_as is not None:
            if isinstance(json_response, list):
                return map(parse_as.parse, json_response)
            else:
                return parse_as.parse(json_response)
        else:
            return json_response


"""
onfleet = Onfleet(key)
onfleet.workers(worker, method="POST")
onfleet.workers['1234'](worker, method="PUT")
onfleet.workers['1234'](method="DELETE")
"""

if __name__ == "__main__":
    on = Onfleet("ab9a9256df0db80d837bf8a85b9a88fa")
#    workers = on.workers()
#    worker = workers[0]
#    print worker.id
    # worker = on.workers['i0TlEqfEk8E65i4dW~0J58VZ']()
    # print worker

    # destination = on.destinations(Destination(address=Address(unparsed="5610 N Scout Island Circle, Austin, TX, 78731, USA")), method="POST")
    # recipient = on.recipients(Recipient(name="John Doe", phone="7862011161"), method="POST")

    destination = Destination(id="BF~2pwPZp3eOPK5qftAqUCLe")
    recipient_id = "QUi7ktEek52OsVkS*0ST0Qt~"

    task = on.tasks(Task(destination=destination.id, recipients=[recipient_id]), method="POST")
    print task


