API Overview
-------------

Schema
+++++++

All resources should have an associated schema. The schema describes the
resource fully. It serves as documentation, specificies the validaty of a resource
and makes it possible to find links to related resources.

Content Type
+++++++++++++

By default all resources return `application/json; schema=<location>` as the
content-type. If other content-types are available, this should be indicated
using `Link` headers.

Link Headers
++++++++++++

Every response should contain link headers to related resources. 

Methods
++++++++++

All resources should respond to OPTIONS requests. 

When a resource responds to GET requests, it should also respond to HEAD requests.

A PUT request replaces the complete resource. When appropriate, it should also be 
possible to create resources using PUT requests.

Partially updating a resource is done with a PATCH request. The content-type of a
patch request is `application/json-patch`.

Status Codes
++++++++++++

By default return a 200 status code. DELETE requests can return a 204. When
a resource is created using a POST request, a 201 status code is returned. Such 
a response should contain a `Location` header pointing to the location of the 
resource.

If a request is handled asynchronously, a 202 status code is returned.

Errors
++++++

Errors should return json describing the errors.

The following status codes should be used. 

+ 400 The request body cannot be parsed
+ 401 Authentication is required for this resource
+ 403 You do not have the correct priviliges
+ 404 The resource does not exists
+ 405 The method is not appropriate for this resource
+ 406 The requested content tpye is not available for this resource
+ 409 The resource already exists
+ 412 The etag does not match the resource
+ 422 An validation error occured

Etags
++++++++

All resources should return a `Etag` header. Requests with `If-Match` / 
`If-None-Match` headers should be handle appropriately.

Versioning
++++++++++

Everry schema associated with a resource has a version. This version is part
of the URI of the schema. This can be used to version the API. To retrieve a specific
version of the resource, specify a older version of the schema in the `Accept` header. 

By default, the latest version is retrieved. Clients are strongly encouraged to
specify a schema in the accept header.

Paging
++++++

Collection resources should return link headers to the previous, next, first 
and last page. 

TODO: How to do paging using GET parameters. How to do sorting / filtering.

Authentication
++++++++++++++

All requests need to be authenticated using an `oauth bearer token`. A token
can be requested from the oauth services. Authorized request are made by adding
an `Authorization` header containing `Bearer <token>`  

Core componenents
+++++++++++++++++

- Documentation browser
  Retrieves json-schemas and compiles it do RST-documents. Makes this documentation
  available through an API. Make this documentation available through as HTML
  interface.

  Resources:
   - Page

  Questions:
  
  + How do we discover resources? 

    The complete API should be discoverable. Every service should provide a
    discription resource. From this discription resource, it should be possible
    to find all the relevant schemas. 

  + How do we create rst from the schemas?

    All schemas should contain the nessecary titles and descriptions that fully 
    describe the resource. The main title and description should describe the 
    resource. Every property in the resource should be described in the property.

- Analytics

  By default all service should emit messages on every api call. The analytics 
  service makes sure these messages end up in a analytics service. These analytics
  should also be available as resources in this service.

  Resources:
  - Resource
  - Application


