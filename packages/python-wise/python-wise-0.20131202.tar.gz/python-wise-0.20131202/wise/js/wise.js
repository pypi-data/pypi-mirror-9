// -*- mode: js; coding: utf-8 -*-

_ = bind(console, console.info);

(function() {
    /*
     * Simple JavaScript Inheritance
     * By John Resig http://ejohn.org/
     * MIT Licensed.
     */

    // Inspired by base2 and Prototype

    var initializing = false;
    var fnTest = /xyz/.test(function(){xyz;}) ? /\b_super\b/ : /.*/;

    // The base Class implementation (does nothing)
    this.Class = function(){};

    // Create a new Class that inherits from this class
    Class.extend = function(prop) {
        var _super = this.prototype;

        // Instantiate a base class (but only create the instance,
        // don't run the init constructor)
        initializing = true;
        var prototype = new this();
        initializing = false;

        // Copy the properties over onto the new prototype
        for (var name in prop) {

	    // Check if we're overwriting an existing function
	    prototype[name] = typeof prop[name] == "function" &&
		typeof _super[name] == "function" && fnTest.test(prop[name]) ?
		(function(name, fn){
		    return function() {
			var tmp = this._super;

			// Add a new ._super() method that is the same method
			// but on the super-class
			this._super = _super[name];

			// The method only need to be bound temporarily, so we
			// remove it when we're done executing
			var ret = fn.apply(this, arguments);
			this._super = tmp;

			return ret;
		    };
		})(name, prop[name]) :
	    prop[name];
        }

        // The dummy class constructor
        function Class() {
	    // All construction is actually done in the init method
	    if ( !initializing && this.init )
		this.init.apply(this, arguments);
        }

        // Populate our constructed prototype object
        Class.prototype = prototype;

        // Enforce the constructor to be what we expect
        Class.prototype.constructor = Class;

        // And make this class extendable
        Class.extend = arguments.callee;

        return Class;
    };

})();


// bind a method to an specific object
// from: http://fitzgeraldnick.com/weblog/26/
function bind(scope, fn) {
    if (!fn)
	throw "Invalid function to bind:", fn

    return function () {
	var args = Array.prototype.slice.call(arguments);
        return fn.apply(scope, args);
    };
};


// from: http://goo.gl/OTwTQi
if (typeof String.prototype.format != 'function') {
    String.prototype.format = function() {
	var args = arguments;
	return this.replace(/{(\d+)}/g, function(match, number) {
	    return (typeof args[number] != 'undefined') ? args[number] : match;
	});
    };
}

// from: http://goo.gl/rw1ku7
if (typeof String.prototype.startsWith != 'function') {
    String.prototype.startsWith = function(str) {
	return this.slice(0, str.length) == str;
    };
}

if (typeof String.prototype.endsWith != 'function') {
    String.prototype.endsWith = function(str) {
	return this.slice(-str.length) == str;
    };
}


Observable = Class.extend({
    init: function() {
	this._observers = [];
    },

    attach: function(observer) {
	if (this._observers.indexOf(observer) != -1)
	    return;
	this._observers.push(observer);
    },

    detach: function(observer) {
	var index = this._observers.indexOf(observer);
	if (index == -1) {
	    return;
	}

	this._observers.splice(index, 1);
    },

    notify: function() {
	var args = Array.prototype.slice.call(arguments);
	for (var i in this._observers) {
	    var obj = this._observers[i];
	    obj.notify.apply(obj, args);
	}
    },
});


wise = {

no_reconnect: false,

_get_typecode: function(value) {
    if (value === undefined || value === null)
	return undefined;

    return value && value["wise_typecode"];
},


Transceiver: Class.extend({
    _reconnect_retries: 15,

    init: function(communicator, endpoint, promise) {
	this._communicator = communicator;
    	this._response_callbacks = {};
    	this._request_id = 0;
	this._endpoint_info = endpoint;

	// FIXME: this attribute may be replaced with a promise that support several
	// fulfill callbacks
	this._waiting_callbacks = [promise];

	this._is_ready = false;
	this._socket_url = "ws://" + endpoint.host +
	    ":" +  endpoint.port + "/" + endpoint.ws_name;

	log.debug("new WebSocket: " + this._socket_url);

	this._create_socket()
            .then(bind(this, this._notify_waiting_callbacks));

	log.debug("Transceiver created");
    },

    // FIXME: transport specific
    _create_socket: function() {
	var self = this;
	var promise = new wise.Promise();
    	var websocket = new WebSocket(this._socket_url);
    	websocket.onopen = function(event) {
	    self._websocket = this;

	    log.debug("Socket opened (" + self._socket_url + "),", event);
	    promise.resolve();

	    websocket.onclose = function(event) {
		if (event.code == 403){
		    log.error("Error on socket:", event.reason);
		    return;
		}

		log.debug("Socket closed:", event);
		if (! wise.no_reconnect)
		    self._try_reconnect();
	    };
    	};
    	websocket.onmessage = function(event) {
	    var message = JSON.parse(event.data);
    	    self._on_ws_message(message);
    	};
	websocket.onerror = function(event) {
	    log.debug("Socket error:", event);
	};

	return promise;
    },

    // FIXME: notify of connection lost
    // FIXME: remove notification when connection is restablished
    _try_reconnect: function() {
	var self = this;
	var connect_count = 0;

	var timer = setInterval(function() {
	    log.info("WebSocket closed, trying to restablish connection (try {0})..."
		     .format(connect_count));

	    self._is_ready = false;
	    delete self._websocket;

	    self._create_socket()
		.then(function() {
		    clearInterval(timer);
		    self._notify_waiting_callbacks();
		});

	    connect_count++;
	    if (connect_count > self._reconnect_retries) {
		log.error("Server connection lost");
		clearInterval(timer);
	    }

	}, 2000);
    },

    // args: request, callback
    send_request: function(args) {
	log.debug("Transceiver send_request: ", args.request);

    	args.request.request_id = this._request_id;
    	this._response_callbacks[this._request_id] = args.callback;

    	if (this._websocket.readyState != WebSocket.OPEN) {
    	    log.error("socket for " + this._websocket.url + " not ready, readyState: " +
		      this._websocket.readyState + ", should be " + WebSocket.OPEN,
		      this._websocket);
    	    return;
    	}

	// FIXME: transport specific: masrshalling
	this._prepare_params(args.request.params);
    	this._websocket.send(JSON.stringify(args.request));
    	this._request_id++;
    },

    link_to_adapter: function(adapter) {
	this._object_adapter = adapter;
    },

    toString: function() {
	return "-w " + this._endpoint_info.ws_name
	    + " -h " + this._endpoint_info.host
	    + " -p " + this._endpoint_info.port;
    },

    _notify_waiting_callbacks: function() {
	this._is_ready = true;
	for (var i=0; i<this._waiting_callbacks.length; i++) {
	    this._waiting_callbacks[i].resolve(this);
	}

	this._waiting_callbacks = [];
    },

    notify_when_ready: function(promise) {
	if (this._is_ready) {
	    promise.resolve(this);
	    return;
	}

	this._waiting_callbacks.push(promise);
    },

    // FIXME: rename: marshall_typecode_seq
    _prepare_params: function(params) {
	if (params == undefined)
	    return;

	for (var i in params)
	    params[i] = this._marshall_typecode(params[i]);
    },

    _marshall_typecode: function(value) {
	if (value instanceof wise.ObjectPrx)
	    return {"wise_typecode": "Proxy",
		    "repr": value.wise_toString()};

	return value;
    },

    _on_ws_message: function(message) {
	log.debug("%cTransceiver Incomming message:",
		  "color:green; font-weight:bold",
		  message);

    	if (message.method !== undefined) {
	    this._process_incoming_invocation(message);
	    return;
	}

    	if (message.result !== undefined) {
	    this._process_incoming_success_reply(message);
	    return;
	}

    	if (message.error !== undefined) {
            this._process_incoming_error_reply(message);
	    return;
	}

    	// invalid protocol format
    	this._report_invalid_message(message);
    },

    // FIXME: rename to "_unmarshall_typecode_seq"
    _unmarshall_params: function(params) {
	var promises = [];
	for (var i in params)
	    promises.push(this._unmarshall_typecode(params[i]))

	return wise.all(promises);
    },

    _unmarshall_typecode: function(value) {
	var typecode = wise._get_typecode(value)

	if (typecode  === undefined)
	    return value;

	if (typecode === "Proxy")
	    return this._communicator.stringToProxy(value["repr"]);
    },

    _process_incoming_invocation: function(message) {
	var self = this;
	if (message.params.length == 0) {
    	    this._perform_request(message);
	    return;
	}

	this._unmarshall_params(message.params)
	    .then(function(params) {
		message.params = params;
    		self._perform_request(message);
	    });
    },

    _perform_request: function(message) {
	log.debug("parse request (", message, ") using:", this._object_adapter);

    	if (! this._object_adapter) {
	    // FIXME: what is that case?
    	    return;
    	}

	try {
    	    var result = this._object_adapter.process_request(message);
	    // FIXME: must marshall result!
	    this._send_response({
		request_id: message.request_id,
		result: result
	    });
	}
	catch (exception) {
	    this._send_response({
		request_id: message.request_id,
		exception: this._to_wise_exception(exception)
	    });
    	}
    },

    _to_wise_exception: function(exception) {
	if (exception instanceof wise.WiseException)
	    return exception;

	return new wise.WiseException("UnknownLocalException", exception.message);
    },

    // args: request_id, result, exception
    _send_response: function(args) {
    	if (this._websocket.readyState != WebSocket.OPEN) {
    	    log.error("socket not ready, state: " + this._websocket.readyState);
    	    return;
    	}

	this._prepare_params(args);
    	this._websocket.send(JSON.stringify(args));
    },

    _process_incoming_success_reply: function(reply) {
	if (wise._get_typecode(reply.result) === undefined) {
	    this._perform_response(reply);
	    return;
	}

	var self = this;
	self._unmarshall_typecode(reply.result)
	    .then(function(result) {
		reply.result = result;
		self._perform_response(reply);
	    });
    },

    _perform_response: function(reply) {
    	var callback = this._response_callbacks[reply.request_id];
    	if (! callback) {
	    // FIXME: callback never deleted!
    	    return;
    	}

	callback.resolve(reply.result);
    	delete this._response_callbacks[reply.request_id];
    },

    _process_incoming_error_reply: function(reply) {
    	var callback = this._response_callbacks[reply.request_id];
    	if (! callback) {
	    // FIXME: callback never deleted
    	    return;
    	}

	var exception = this._unmarshall_exception(reply.error);
	if (callback.err_callbacks.length === 0) {
	    log.error("Error received, but not Promise error callbacks defined:",
		      exception);
	}

	callback.reject(exception);
    	delete this._response_callbacks[reply.request_id];

	// FIXME: is this required/convenient ??
	// throw exception;
    },

    _unmarshall_exception: function(error) {
	return new wise.WiseException(error[0], error[1]);
    },

    _report_invalid_message: function(message) {
	throw new wise.WiseException("ProtocolException",
				     "invalid message recived! (" + JSON.stringify(message) + ")");

    	log.error("invalid message recived! (" + JSON.stringify(message) + ")");
    },
}),

TransceiverFactory: Class.extend({
    init: function(communicator) {
	this._transceivers = {};
	this._communicator = communicator;
    },

    // used by stringToProxy
    get_transceiver: function(endpoint) {
	log.debug("TransceiverFactory: get_transceiver: '{0}'".format(endpoint.ws_name));

	var transceiver = this._transceivers[endpoint.ws_name];
	var promise = new wise.Promise();

	if (transceiver) {
	    transceiver.notify_when_ready(promise);
	    return promise;
	}

	this._new_transceiver(endpoint, promise);
	return promise;
    },

    // used by createObjectAdapter
    create_transceiver: function(endpoint) {
	log.debug("TransceiverFactory: create_transceiver: '{0}'"
		  .format(endpoint.ws_name));

	var transceiver = this._transceivers[endpoint.ws_name];
	if (transceiver) {
	    throw "AlreadyUsedEndpoint";
	}

	// contact with server and create a new websocket
	if (! this._server_admin) {
	    throw ("Could not create transceiver: " +
		   "Communicator not fully initialized");
	}

	this._server_admin.create_socket(endpoint)
	    .then(bind(this, on_create_socket_response));

	var promise = new wise.Promise();
	function on_create_socket_response() {
	    this._new_transceiver(endpoint, promise);
	}

	return promise;
    },

    _new_transceiver: function(endpoint, promise) {
	log.debug("TransceiverFactory._new_transceiver,", endpoint.ws_name);
	var transceiver = new wise.Transceiver(this._communicator, endpoint, promise);
	this._transceivers[endpoint.ws_name] = transceiver;
    },
}),

// FIXME: improve this parser (and test this)
EndpointInfo: Class.extend({
    init: function(endpoint, defaults, oaendpoint) {
	if (endpoint == undefined)
	    endpoint = "";

	endpoint = endpoint.trim();

	// remove two spaces in string
	while (true) {
	    if (endpoint.indexOf("  ") == -1)
		break;
	    endpoint = endpoint.replace("  ", " ");
	}

	// split components
	var index = -1;
	var items = endpoint.split(" ");

	// web service locator
	this.ws_name = "";
	index = items.indexOf("-w");
	if (index != -1) {
	    this.ws_name = items[index + 1];
	    items.splice(index, 2);
	}

	if (this.ws_name == "") {
	    if (oaendpoint)
		this.ws_name = this._get_random_ws_name();
	    else
		throw "Invalid endpoint, no WS especified";
	}

	// hostname
	this.host = "";
	index = items.indexOf("-h");
	if (index != -1) {
	    this.host = items[index + 1];
	    items.splice(index, 2);
	}

	if (this.host == "") {
	    if (! defaults || ! defaults.host)
		throw "Invalid endpoint, no host especified";
	    this.host = defaults.host
	}

	// port
	this.port = "";
	index = items.indexOf("-p");
	if (index != -1) {
	    this.port = items[index + 1];
	    items.splice(index, 2);
	}

	if (this.port == "") {
	    if (! defaults || ! defaults.port)
		throw "Invalid endpoint, no port especified";
	    this.port = defaults.port;
	}

	for (var i in items) {
	    if (items[i])
		throw "Invalid endpoint, unknown params: " + items;
	}
    },

    _get_random_ws_name: function() {
	return wise.Util.S4() + wise.Util.S4();
    },
}),

ObjectAdapter: Class.extend({
    init: function(transceiver) {
    	this._asm = {};

	this._transceiver = transceiver;
	this._transceiver.link_to_adapter(this);
    },

    add: function(servant, identity) {
    	this._asm[identity] = servant;

	servant.wise_getMethodNames = function() {
	    var res = [];
	    for(var m in this)
		if ((typeof this[m] == "function")
		    && (m != "constructor")
		    && (m != "wise_getMethodNames"))
		    res.push(m)
	    return res;
	};

	log.debug("Adding object: " + identity);
	return this.createProxy(identity);
    },

    addWithUUID: function(servant) {
	var identity = wise.Util.generate_UUID();
	return this.add(servant, identity);
    },

    remove: function(identity) {
	log.debug("Removing object: " + identity);
	delete this._asm[identity];
    },

    createProxy: function(identity) {
	return new wise.ObjectPrx({
	    identity: identity,
	    transceiver: this._transceiver
	});
    },

    process_request: function(request) {
    	log.debug("request received: " + request.identity + "."
    		  + request.method, request.params);

	var obj = this._find_object(request.identity);

	if (!(request.method in obj)) {
	    msg = "Unknown method: '" + request.method + "'";
	    log.error(msg);
	    throw new wise.WiseException("OperationNotExistException", msg);
	}

	return obj[request.method].apply(obj, request.params);
    },

    _find_object: function(identity) {
    	var object = this._asm[identity];
    	if (! object) {
    	    msg = "Unknown object: '" + identity + "'";
    	    log.error(msg);
	    throw new wise.WiseException("ObjectNotExistException", msg);
    	}
    	return object;
    },
}),

ObjectPrx: Class.extend({
    // FIXME: this is actually two different constructors
    // args: (identity, transceiver) || base
    init: function(args) {
	if (args.base) {
	    this._identity = args.base.wise_getIdentity();
	    this._transceiver = args.base.wise_getTransceiver();
	    return;
	}

    	this._identity = args.identity;
    	this._transceiver = args.transceiver;
    },

    wise_invoke: function(args) {
    	args.request.identity = this._identity;
    	this._transceiver.send_request(args);
    },

    wise_getTransceiver: function() {
    	return this._transceiver;
    },

    wise_getIdentity: function() {
    	return this._identity;
    },

    wise_toString: function() {
	return this._identity + " " + this._transceiver.toString();
    },
}),

Util: {
    // taken from: http://guid.us/GUID/JavaScript
    S4: function() {
	return (((1+Math.random())*0x10000)|0).toString(16)
	    .substring(1);
    },

    generate_UUID: function() {
	var S4 = wise.Util.S4;
	return (S4() + S4() + "-" + S4() + "-4" + S4().substr(0,3)
		+ "-" + S4() + "-" + S4() + S4() + S4()).toUpperCase();
    },
},

Logger: Class.extend({
    init: function(level) {
	this._observers = [];

	if (level == undefined)
	    level = 1;

	this._level = level;
    },

    attach: function(observer) {
	this._observers.push(observer);
    },

    set_level: function(level) {
	this._level = level;
    },

    debug: function() {
	if (this._level > 0)
	    return;

	this._notify(arguments, 'debug');
    },

    info: function() {
	if (this._level > 1)
	    return;

	this._notify(arguments, 'info');
    },

    warning: function() {
	if (this._level > 2)
	    return;

	this._notify(arguments, 'warn');
    },

    error: function() {
	if (this._level > 3)
	    return;

	this._notify(arguments, 'error');
    },

    _notify: function(args, method) {
	args = Array.prototype.slice.call(args, 0);

	for (var i in this._observers) {
	    var o = this._observers[i];
	    if (o[method] == undefined)
		continue;
	    o[method].apply(o, args);
	}
    },
}),

// Add a callback to be called when a communicator is created
on_communicator_ready: function(callback) {
    if (this._last_communicator) {
	callback(this._last_communicator);
	return;
    }

    if (this._waiting_for_init === undefined) {
	this._waiting_for_init = [];
    }

    this._waiting_for_init.push(callback);
},

Communicator: Class.extend({
    init: function(args) {
	this._host = args.host;
	this._port = args.port;
	this._adapters = {};
	this._transceiverFactory = new wise.TransceiverFactory(this);
    },

    // args: name, endpoint, callback
    createObjectAdapter: function(name, endpoint) {
	if (name in this._adapters)
	    throw "AlreadyRegisteredException"

	this._transceiverFactory.create_transceiver(
	    new wise.EndpointInfo(endpoint, {host: this._host, port: this._port}, true)
	).then(bind(this, on_create_transceiver_response))

	var promise = new wise.Promise();
	function on_create_transceiver_response(transceiver) {
	    var adapter = new wise.ObjectAdapter(transceiver);
	    this._adapters[name] = adapter;
	    promise.resolve(adapter);
	}

	return promise;
    },

    stringToProxy: function(str_proxy) {
	log.debug("stringToProxy: '{0}'".format(str_proxy));
	var fields = this._get_proxy_fields(str_proxy);

	this._transceiverFactory.get_transceiver(fields.endpoint)
	    .then(bind(this, on_get_transceiver_response));

	var promise = new wise.Promise();
	function on_get_transceiver_response(transceiver) {
	    var WisePrx = wise.newDerivedProxy({
	    	methods: ['wise_getMethodNames']
	    });

	    var base = new WisePrx({
	    	identity: fields.identity,
	    	transceiver: transceiver,
	    });

	    // build dynamic methods for remote object
	    base.wise_getMethodNames()
		.then(on_getMethodNames_response,
		      on_getMethodNames_error);

	    function on_getMethodNames_response(result) {
		result = result.concat(['wise_getMethodNames'])
		var DerivedPrx = wise.newDerivedProxy({
		    methods: result
		});
		var proxy = new DerivedPrx({
		    identity: fields.identity,
		    transceiver: transceiver
		});

		promise.resolve(proxy);
	    }

	    function on_getMethodNames_error(e) {
		promise.reject(e);
	    }
	}

	return promise;
    },

    _get_proxy_fields: function(proxy) {
	// example: "ObjectId -w ws -h 127.0.0.1 -p 8080"

	proxy = proxy.trim();

	// split identity and endpoint
	var items = proxy.split(" ");
	var identity = items[0];
	var endpoint = items.slice(1).join(" ");

	return {
	    identity: identity,
	    endpoint: new wise.EndpointInfo(
		endpoint,
		{host: this._host, port: this._port}),
	};
    },

    ready: function() {
	// notify to others that this part is ready
	var div = document.createElement('div');
	div.id = 'wiseReady';
	var body = document.querySelector('body');
	body.appendChild(div);

	wise._last_communicator = this;
	if (wise._waiting_for_init !== undefined) {
	    for (var i in wise._waiting_for_init) {
		wise._waiting_for_init[i](this);
	    }
	    wise._waiting_for_init.length = 0;
	}
    },
}),

// args: host, port, on_ready
initialize: function(host, port) {
    if (port == undefined)
	port = location.port;

    if (host == undefined)
	host = location.hostname;

    // create root logger for Wise
    log = new wise.Logger();
    log.set_level(0);
    if (typeof console != "undefined") {
	log.attach(console);
    }

    // create communicator
    var ic = new wise.Communicator({ host: host, port: port });

    // create server admin proxy
    ic.stringToProxy("WiseAdmin -w wise -h "+ host +" -p "+ port)
	.then(bind(this, on_stringToProxy_response));

    // response: proxy
    var promise = new wise.Promise();
    function on_stringToProxy_response(proxy) {
	wise.TransceiverFactory.prototype._server_admin = proxy;

	// finish intialization
	promise.resolve(ic);
	ic.ready()
    }

    return promise;
},


// args: methods
newDerivedProxy: function(args) {
    var methods = {};

    function new_method(name) {
	return function() {
	    var promise = new wise.Promise();
	    this.wise_invoke({
		request: {
		    method: name,
		    params: Array.prototype.slice.call(arguments),
		},
		callback: promise
	    });
	    return promise;
	};
    }

    for (var i in args.methods) {
	var name = args.methods[i];
	methods[name] = new_method(name);
    }

    return wise.ObjectPrx.extend(methods);
},


Promise: Class.extend({
    init: function() {
	this.value = null;
	this.reason = null;
	this.ok_callbacks = [];
	this.err_callbacks = [];
    },

    then: function(onFulfilled, onRejected) {
	var promise = new wise.Promise();

	if (typeof(onFulfilled) !== 'function')
	    onFulfilled = undefined;
	else if (this.value)
	    this._exec_callback(promise,
				onFulfilled, this.value);

	if (typeof(onRejected) !== 'function')
	    onRejected = undefined;
	else if (this.reason)
	    this._exec_callback(promise,
				onRejected, this.reason);

	if (onFulfilled !== undefined)
	    this.ok_callbacks.push({'promise': promise, 'func': onFulfilled});

	if (onRejected !== undefined)
	    this.err_callbacks.push({'promise': promise, 'func': onRejected});

	return promise;
    },

    "catch": function(onRejected) {
	return this.then(undefined, onRejected);
    },

    check_resolved: function() {
	if (this.value !== null || this.reason !== null)
	    throw new Error("Promise already resolved/rejected" + this);
    },

    resolve: function(value) {
	this.check_resolved();
	this.value = value;

	var self = this;
	this.ok_callbacks.map(function(cb) {
	    self.outctx(cb.promise, cb.promise.resolve, cb.func, value);
	});
    },

    reject: function(reason) {
	this.check_resolved();
	this.reason = reason;

	var self = this;
	this.err_callbacks.map(function(cb) {
	    self.outctx(cb.promise, cb.promise.reject, cb.func, reason);
	});
    },

    outctx: function(promise, method, cb, value) {
	var self = this;
	setTimeout(function() {
	    if (cb === undefined)
		return bind(promise, method)(value);

	    bind(self, self._exec_callback)(promise, cb, value);
	}, 0);
    },

    _exec_callback: function(promise, func, value) {
	try {
	    var x = func(value);
	    this._PRP(promise, x);
	} catch (e) {
	    console.error("Exception in promise callback: " + e.stack);
	    console.error(e);
	    promise.reject(e);
	}
    },

    _PRP: function(promise, x) {
	if (promise === undefined)
	    return;

	if (promise === x) {
	    promise.reject(new TypeError());
	    return;
	}

	// If x is a promise, adopt its state [3.4]:
	if (typeof(x) === 'Promise') {
	    x.then(promise.resolve, promise.reject);
	    return;
	}

	// If x is not an object or function, or x is null, fulfill promise with x.
	if (typeof(x) != 'function' && typeof(x) != 'object' || x === null) {
	    promise.resolve(x);
	    return;
	}

	// if x is an object or function
	try {
	    var then = x.then;
	} catch (e) {
	    promise.reject(e);
	    return;
	}

	if (typeof(then) != 'function') {
	    promise.resolve(x);
	    return;
	}

	var resolved = false;
	try {
	    bind(x, then)(resolvePromise, rejectPromise);
	} catch(e) {
	    if (!resolved) {
		promise.reject(e);
		resolved = true;
	    }
	    return;
	}

	function resolvePromise(y) {
	    if (!resolved)
		this._PRP(promise, y);
	    resolved = true;
	}
	function rejectPromise(r) {
	    if (!resolved)
		promise.reject(r);
	    resolved = true;
	}
    }
}),

map: function(array, callable) {
    // https://github.com/cujojs/when/blob/master/when.js

    function resolveOne(item, i) {
	cast(item).then(callable).then(
	    function(retval) {
		results[i] = retval;
		if (!--len)
		    promise.resolve(results);
	    },

	    function(error) {
		log.error("error on wise.map:", error.message);
	    }
	);
    }

    function cast(x) {
        if (x instanceof wise.Promise)
	    return x;

	var p = new wise.Promise();
	p.resolve(x);
	return p.then(wise.identity);
    }

    var promise = new wise.Promise();
    var results = [];
    var len = array.length;

    for (var i in array) {
	resolveOne(array[i], i);
    }

    return promise;
},

all: function(array) {
    return wise.map(array, wise.identity);
},

identity: function(x) {
    return x;
},

WiseException: function(name, message) {
    this.name = name;
    this.message = message;
},

}; // wise namespace

wise.WiseException.prototype = new Error();
wise.WiseException.prototype.constructor = wise.WiseException;

window.onload = function() {
    if (typeof wise_application == "undefined") {

	// no log created yet, so try to say something
	if (typeof console != "undefined") {
	    console.warn("'wise_application' is not defined, nothing to do");
	}

	return;
    }

    wise.initialize().then(function(ws) {
	wise_application(ws);
    });
}
