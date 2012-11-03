/*
 * Format for Selenium Remote Control Python client.
 */

var subScriptLoader = Components.classes["@mozilla.org/moz/jssubscript-loader;1"].getService(Components.interfaces.mozIJSSubScriptLoader);
subScriptLoader.loadSubScript('chrome://selenium-ide/content/formats/remoteControl.js', this);

this.name = "chrome://selenium-ide/content/formats/python-nagios2-plugin";

function testMethodName(testName) {
	return "run";
}

notOperator = function() {
	return "not ";
};

string = function(value) {
	value = value.replace(/\\/g, '\\\\');
	value = value.replace(/\"/g, '\\"');
	value = value.replace(/\r/g, '\\r');
	value = value.replace(/\n/g, '\\n');
	var unicode = false;
	for (var i = 0; i < value.length; i++) {
		if (value.charCodeAt(i) >= 128) {
			unicode = true;
		}
	}
	return (unicode ? 'u' : '') + '"' + value + '"';
}

function assertTrue(expression) {
	return expression.toString();
}

function assertFalse(expression) {
	return expression.toString();
}

function verify(statement) {
	return  statement;
}

function verifyTrue(expression) {
	return verify(assertTrue(expression));
}

function verifyFalse(expression) {
	return verify(assertFalse(expression));
}

function joinExpression(expression) {
    return "','.join(" + expression.toString() + ")";
}

function assignToVariable(type, variable, expression) {
	return variable + " = " + expression.toString();
}

function waitFor(expression) {
	return "for i in range(60):\n" +
		indents(1) + "try:\n" +
        indents(2) + "if " + expression.toString() + ": break\n" +
		indents(1) + "except: pass\n" +
		indents(1) + 'time.sleep(1)\n' +
        'else: self.fail("time out")';
}

function assertOrVerifyFailure(line, isAssert) {
	return "try: " + line + "\n" +
		"except: pass\n" +
		'else: self.fail("expected failure")';
}

Equals.prototype.toString = function() {
	return this.e1.toString() + " == " + this.e2.toString();
};

Equals.prototype.assert = function() {
	return "self.assertEqual(" + this.e1.toString() + ", " + this.e2.toString() + ")";
};

Equals.prototype.verify = function() {
	return verify(this.assert());
};

NotEquals.prototype.toString = function() {
	return this.e1.toString() + " != " + this.e2.toString();
};

NotEquals.prototype.assert = function() {
	return "self.assertNotEqual(" + this.e1.toString() + ", " + this.e2.toString() + ")";
};

NotEquals.prototype.verify = function() {
	return verify(this.assert());
};

RegexpMatch.prototype.toString = function() {
	var str = this.pattern;
	if (str.match(/\"/) || str.match(/\n/)) {
		str = str.replace(/\\/g, "\\\\");
		str = str.replace(/\"/g, '\\"');
		str = str.replace(/\n/g, '\\n');
		return '"' + str + '"';
	} else {
		str = 'r"' + str + '"';
	}
	return "re.search(" + str + ", " + this.expression + ")";
};

function pause(milliseconds) {
	return "time.sleep(" + (parseInt(milliseconds, 10) / 1000) + ")";
}

function echo(message) {
	return "print(" + xlateArgument(message) + ")";
}

function statement(expression) {
	return expression.toString();
}

function array(value) {
	var str = '[';
	for (var i = 0; i < value.length; i++) {
		str += string(value[i]);
		if (i < value.length - 1) str += ", ";
	}
	str += ']';
	return str;
}

function nonBreakingSpace() {
    return "u\"\\u00a0\"";
}

CallSelenium.prototype.toString = function() {
	var result = '';
	if (this.negative) {
		result += 'not ';
	}
	if (options.receiver) {
		result += options.receiver + '.';
	}
	result += underscore(this.message);
	result += '(';
	for (var i = 0; i < this.args.length; i++) {
		result += this.args[i];
		if (i < this.args.length - 1) {
			result += ', ';
		}
	}
	result += ')';
	return result;
};

function formatFooter(testCase) {
    className = testCase.getTitle();
    var formatLocal = testCase.formatLocal(this.name);
    formatLocal.footer = options.footer;
   // return formatLocal.footer.replace(/\$\{className\}/g, className);
    return formatLocal.footer + "doidosomething";
}


this.options = {
	receiver: "selenium_proxy",
	rcHost: "localhost",
	rcPort: "4444",
	environment: "*chrome",
	header:
        '#!/usr/bin/env python\n\n'+
	'from seymour.seleniumbaserunner import SeleniumBaseRunner\n' +
        'import re\n' +
	'\n' +
	'class NagiosRunner(SeleniumBaseRunner):\n' +
	'    \n' +
	'    def ${methodName}(self):\n' +
	'        ${receiver} = self.selenium_proxy\n',
	footer:
	'    \n' +
	'\n' +
	'if __name__ == "__main__":\n' +
        '    runnable = NagiosRunner()\n' +
	'    runnable.execute()\n',
    indent:	'4',
	initialIndents: '2'
};
