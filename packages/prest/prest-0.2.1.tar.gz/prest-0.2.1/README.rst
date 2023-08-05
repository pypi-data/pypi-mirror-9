prest documentation
===================

Writing python API for REST service is a quite boring task.
prest is intended to do all monkey work for you. Take
a look at example:

.. code:: python
	from prest import EasyRestBase, GET, POST, DELETE


	class MyRestfullAPI(EasyRestBase):
	    list_objs = GET('objects')
	    get_obj = GET('objects/{0}')
	    del_obj = DELETE('objects/{0}')
	    create_obj = POST('objects')
	    select_objs = GET('objects/filter')
	    objs_by_type = GET('objects/{type}')


	conn = MyRestfullAPI("http://some.api.com/my_api/v2.0")

	print conn.list_objs()

	obj_id = conn.create_obj()['id']
	conn.select_objs(color='read')
	conn.del_obj(obj_id)
	conn.objs_by_type(type='red')


There 6 basic functions for http methods:
GET, POST, PUT, PATCH, DELETE, HEAD. Each of them
requires relative path and returns function. This 
function, in its turn, gets connection and a set of 
parameters, insert some of them in url (if there a placeholders), 
attach all the rest as GET/POST parameters and make 
a http request. Receive a result, unpack it and return.

So you need only one line to make an API func for 
each REST call.
	
In case if result of GET/... calls is assigned to
class method of class inherited from PRestBase
then call gets connection from self. 

Meanwhile you can use it separately:

.. code:: python
	from prest import GET, Urllib2HTTP_JSON

	get_cluster_data = GET('data/{cluster_id}')
	conn = Urllib2HTTP_JSON("http://my_api.org")
	print get_cluster_data(conn, cluster_id=11)


Both Urllib2HTTP_JSON and PRestBase
accepts dictionary of additional headers end echo
parameters. Urllib2HTTP_JSON uses json.dumps and 
json.loads to serialize and deserialize data accordingly.

There also an object-oriented API - please take
a look on test_prest.py. I wrote no documentation 
for it, as it currently breaks 17th rule of python Zen.

