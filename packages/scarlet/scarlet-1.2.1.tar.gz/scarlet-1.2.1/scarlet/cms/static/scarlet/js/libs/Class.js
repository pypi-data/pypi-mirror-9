// ## Simple JavaScript Inheritance
// - By John Resig http://ejohn.org/
// - MIT Licensed.
/* class.js */

// Inspired by base2 and Prototype
define(function () {
	var initializing = false,
		fnTest = (/xyz/).test(function () {
			var xyz;
		}) ? (/\bsup\b/) : (/.*/);

	// The base Class implementation (does nothing)
	var Class = function () {};

	// Create a new Class that inherits from this class
	function extend(prop, events) {
		var sup = this.prototype,
			This = this,
			prototype, name, tmp, ret, func;

		// Instantiate a base class (but only create the instance,
		// don't run the init constructor)
		initializing = true;
		prototype = new This();
		initializing = false;

		// Copy the properties over onto the new prototype
		for (name in prop) {
			if (prop.hasOwnProperty(name)) {
				func = prop[name];

				// Check if we're overwriting an existing function
				prototype[name] = (typeof func === "function") && (typeof sup[name] === "function") && fnTest.test(func) ? (function (name, fn) {
					return function () {
						tmp = this.sup;

						// Add a new .sup() method that is the same method
						// but on the super-class
						this.sup = sup[name];

						// The method only need to be bound temporarily, so we
						// remove it when we're done executing
						ret = fn.apply(this, arguments);
						this.sup = tmp;

						return ret;
					};
				}(name, func)) : func;
			}
		}

		prototype.vars = $.extend(true, {}, this.prototype.vars, prototype.vars); // inherit vars

		// The dummy class constructor
		function SubClass(vars) {

			this.vars = $.extend(true, {}, this.vars, vars); // override this.vars object with passed argument
			
			// All construction is actually done in the init method
			if (!initializing && this.init) {
				this.init.apply(this, arguments);
			}
		}

		// Populate our constructed prototype object
		SubClass.prototype = prototype;

		// Enforce the constructor to be what we expect
		SubClass.constructor = SubClass;

		// And make this class extendable
		SubClass.extend = extend;

		if (typeof events === 'object') {
			$.extend(SubClass, events);
		}

		return SubClass;
	};

	Class.extend = extend;

	return Class;
});
