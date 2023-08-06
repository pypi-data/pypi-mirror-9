![PAYMILL icon](https://static.paymill.com/r/335f99eb3914d517bf392beb1adaf7cccef786b6/img/logo-download_Light.png)
# paymill-python

Python wrapper for PAYMILL API(beta)

## Getting started

- If you are not familiar with PAYMILL, start with the [documentation](https://www.paymill.com/en-gb/documentation-3/).
- Install the latest release.
- Check the API [reference](https://www.paymill.com/en-gb/documentation-3/reference/api-reference/).
- Check the tests.


## Installation

After checking out the project navigate to the root directory and execute following line:

```
 pip install . -r requirements.txt
```

## What's new

We have released version 1.1.0 which is coded directly to the PAYMILL API v2.1 and is Py2&3 compatible.This version is no longer backwards compatible with the pymill fork from https://github.com/kliment/pymill. If you need to be PAYMILL API v2.0 compatible please use https://github.com/paymill/paymill-python/tree/v0.1.2.

## Usage

Initialize the library by providing your api key:
```python
   paymill_context = paymill.PaymillContext('<YOUR PRIVATE API KEY>');
```
PaymillContext loads the context of PAYMILL for a single account, by providing a merchants private key. It creates 8 services, which represents the PAYMILL API:
 * ClientService
 * OfferService
 * PaymentService
 * PreauthorizationService
 * RefundService
 * SubscriptionService
 * TransactionService
 * WebhookService

These services should not be created directly. They have to be obtained by the context's accessors.

### Using services


In all cases, you'll use the predefined service classes to access the PAYMILL API.

To fetch a service instance, call *service name* accessor from paymill_context, like
```python
 client_service = paymill_context.get_client_service();
```
Every service instance provides basic methods for CRUD functionality.

### Creating objects

Every service provides instance factory methods for creation. They are very different for every service, because every object can be created in a different way. The common pattern is
```python
 xxx_service.create_XXX(params...);
```
For example: client can be created with two optional parameters: *email* and *description*. So we have four possible methods to create the client:
```python
 #creates a client without email and description
 client_service.create()
```
```python
 #creates a client with email
 client_service.create(email='john.rambo@paymill.com')
```
```python
 #creates a client with description
 client_service.create(description='CRM Id: fake_34212')
```
```python
 #creates a client with email and description
 client_service.create(email='john.rambo@paymill.com', description='CRM Id: fake_34212')
```

### Retrieving objects

You can retrieve an object by using the get() method with with the instance itself:
```python
 client_service.detail(client);
```
This method throws an PMError if there is no client under the given id.

### Retrieving lists

To retrieve a list you may simply use the list() method:
```python
 clients = client_service.list();
```
You may provide a filter and order to list method:
```python
 clients = client_service.list(
     order=paymill.models.client.Client.Order.created_at().desc(),
     filtr=paymill.models.client.Client.Filter.by_email('john.rambo@paymill.com'))
```
This will load only clients with email john.rambo@paymill.com, order descending by creation date.

### Updating objects

In order to update an object simply call a service's update() method:
```python
 client_service.update(client);
```

### Deleting objects

You may delete objects by calling the service's delete() method with an object instance.
```python
 client_service.remove(client);
```

## Changelog

### 1.1
* Support for Py3
* FilterList added for filter combination 
* Bug fixing & code improvements

### 1.0
* New implementation from scratch that conforms to PAYMILL API v2.1

## License

Copyright 2014 PAYMILL GmbH.

MIT License (enclosed)
