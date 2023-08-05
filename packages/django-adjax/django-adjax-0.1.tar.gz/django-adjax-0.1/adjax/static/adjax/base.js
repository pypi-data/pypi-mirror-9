var adjax = (function () {
    var utils = (function() {
        /*
         * Equivalent to python's zip(...)
         *
         * zip([
         *     ['a', 'b', 'c'],
         *     [1, 2, 3],
         * ])
         *
         * returns [
         *     ['a', 1],
         *     ['b', 2],
         *     ['c', 3],
         * ]
         */
        var zip = function (arrays) {
            return Array.apply(
                null, Array(arrays[0].length)
            ).map(function (_, i) {
                return arrays.map(function (array) {
                    return array[i]
                });
            });
        };

        /*
         * Equivalent to python's dict(...)
         *
         * obj([
         *     ['a', 1],
         *     ['b', 2],
         *     ['c', 3],
         * ])
         *
         * returns {
         *     'a': 1,
         *     'b': 2,
         *     'c': 3,
         * }
         */
        var obj = function (array) {
            var data = {};
            array.forEach(function (item) {
                data[item[0]] = item[1];
            });
            return data;
        };

        /**
         * Get the value of the specified cookie
         */
        var getCookie = function (name) {
            var value = '; ' + document.cookie;
            var parts = value.split('; ' + name + '=');
            if (parts.length == 2) {
                return parts.pop().split(';').shift();
            }
        };

        return {
            'zip': zip,
            'obj': obj,
            'getCookie': getCookie,
        };
    })();

    /**
     * Error
     */
    var Error = function (message) {
        this.message = message;
    };

    Error.prototype.toString = function () {
        return 'ADJAX: ' + this.message;
    };

    /**
     * Custom type
     */
    var Type = function (encode, decode) {
        this.encode = encode;
        this.decode = decode;
    };

    /**
     * Object capable of serializing custom types
     */
    var Serializer = function (typeName) {
        this.typeName = typeName;
        this.types = {};
    };

    Serializer.INTERNAL_TYPE_NAME = '__name__';

    /**
     * Register custom type
     */
    Serializer.prototype.register = function (name, constructor, type) {
        constructor[Serializer.INTERNAL_TYPE_NAME] = name;
        this.types[name] = type;
    };

    /**
     * Encode data to JSON
     */
    Serializer.prototype.encode = function (data) {
        return JSON.stringify(data, (function (key, value) {
            if (key !== '' && value && typeof value === 'object') {
                var name = value.constructor[Serializer.INTERNAL_TYPE_NAME];
                if (name in this.types) {
                    var data = this.types[name].encode(value);
                    data[this.typeName] = name;
                    return data;
                }
            }
            return value;
        }).bind(this));
    };

    /**
     * Decode data from JSON
     */
    Serializer.prototype.decode = function (data) {
        return JSON.parse(data, (function (key, value) {
            if (value && typeof value === 'object' &&
                    value[this.typeName] !== undefined) {
                var name = value[this.typeName];
                if (this.types[name] === undefined) {
                    throw new Error(
                        "Custom type '" + name + "' not implemented");
                }
                return this.types[name].decode(value);
            }
            return value;
        }).bind(this));
    };

    /**
     * Interface object
     */
    var Interface = function (data, views, typeName) {
        this.serializer = new Serializer(typeName);
        this.data = data;
        this.views = views;
        this.pipeline = [];
        this.apps = {};

        for (var app in views) {
            this.apps[app] = {};
            for (var name in views[app]) {
                this.apps[app][name] = this.getView(app, name);
            }
        }
    };

    /**
     * Register XHR pipeline function
     */
    Interface.prototype.register = function (func) {
        this.pipeline.push(func);
    };

    /**
     * Create function for calling the specified view
     */
    Interface.prototype.getView = function (app, name) {
        if (this.views[app] === undefined) {
            throw new Error("App '" + app + "' does not exist");
        }

        if (this.views[app][name] === undefined) {
            throw new Error(
                "View '" + name + "' does not exist in app '" + app + "'");
        }

        var view = this.views[app][name];

        return (function () {
            var callback;
            var values = Array.prototype.slice.call(arguments, 0);
            if (typeof arguments[arguments.length - 1] === 'function') {
                callback = values.pop();
            }
            var data = utils.obj(utils.zip([view['args'], values]));

            var xhr = new XMLHttpRequest();
            xhr.open('POST', view['url']);
            if (callback) {
                xhr.onreadystatechange = (function () {
                    if (xhr.readyState === 4) {
                        var data = this.serializer.decode(xhr.responseText);
                        callback(data);
                    }
                }).bind(this);
            }

            this.pipeline.forEach(function (item) {
                item(xhr);
            });

            xhr.send(this.serializer.encode(data));
        }).bind(this);
    };

    return {
        'utils': utils,

        'Type': Type,
        'Serializer': Serializer,
        'Interface': Interface,
    }
})();
