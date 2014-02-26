# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import requests
import urlparse

from zest_exceptions import (
    ZestAssertStatusCode,
    ZestAssertLength,
    ZestAssertHeader,
    ZestAssertBody
)

def load(data):
    """ Load a dictionary into a new instance of ZestScript. """

    z = ZestScript()
    for z_attr in z.__slots__:
        try:
            if z_attr == "statements":
                for statement in data[z_attr]:
                    s = ZestStatement(zest=z)
                    for s_attr in s.__attributes__:
                        setattr(s, s_attr, statement.get(s_attr))
                    z.statements.append(s)
            else:
                setattr(z, z_attr, data.get(z_attr))
        except KeyError as e:
            raise KeyError("{attr} is missing from the import Zest script.".format(
                                attr=z_attr))
    return z

class ZestScript(object):
    """ Interface for Zest script. """

    # only the following top-level attributes are allowed.
    __slots__ = ["type", "about", "zestVersion", "generatedBy",
        "title", "description", "prefix", "parameters", "statements",
        "doSequence", "authentication", "index", "elementType", "report"]

    ZEST_VERSION = 0.3
    GENERATED_BY = "PyZest"
    ABOUT = "This is a Zest script generated by the py-zest script."
    TITLE = "Unspecified Zest script"
    DESCRIPTION = "Unspecified Zest script"
    ELEMENT_TYPE = "ZestScript"
    ZEST_TYPE = "StandAlone"

    def __init__(self, about=ABOUT, zestVersion=ZEST_VERSION, \
        generatedBy=GENERATED_BY, title=TITLE, description=DESCRIPTION, \
        prefix=None, type=ZEST_TYPE, parameters=None, statements=None, \
        doSequence=False, authentication=None, index=0, elementType=ELEMENT_TYPE):

        self.type = type
        self.about = about
        self.zestVersion = zestVersion
        self.generatedBy = generatedBy
        self.title = title
        self.description = description
        self.prefix = prefix
        self.parameters = parameters
        self.statements = statements or []
        self.doSequence = doSequence
        self.authentication = authentication or []
        self.index = index
        self.elementType = elementType
        # this stores the result after run
        self.report = None

    def run(self):
        self.report = {"passed": 0, "failed": 0, "assertions": []}
        for statement in self.statements:
            result = statement.run()
            self.report["assertions"].append(result)
        passes, fails = self._count_pass_fail(self.report["assertions"])
        self.report["passed"] = passes
        self.report["failed"] = fails

    def _count_pass_fail(self, assertions):
        passes = 0
        fails = 0
        for statement_assert in assertions:
            for assertion in statement_assert["assertions"]:
                if assertion["passed"] is True:
                    passes += 1
                else:
                    fails += 1
        return passes, fails

    def to_dict(self):
        script = dict(
            type = self.type,
            about = self.about,
            zestVersion = self.zestVersion,
            generatedBy = self.generatedBy,
            title = self.title,
            description = self.description,
            prefix = self.prefix,
            parameters = self.parameters,
            elementType = self.elementType,
            statements = self.statements,
            index = self.index,
            authentication = self.authentication,
        )
        return script

    def __str__(self):
        return str(self.to_dict())

    def __unicode__(self):
        return unicode(self.to_dict())

    def __repr__(self):
        return repr(self.to_dict())

class ZestStatement(object):
    """ Interface for Zest statement. """

    # only the following attributes are allowed.
    __attributes__ = ["url", "data", "method", "headers", "response",
        "assertions", "transformations", "index", "elementType"]

    def __init__(self, url=None, data=None, method=None, headers=None,
        response=None, assertions=None, transformations=None,
        index=None, elementType="ZestRequest", zest=None):

        self.zest = zest
        self.url = url
        self.data = data
        self.method = method
        self.headers = headers
        self.response = response or {}
        self.assertions = assertions or []
        self.transformations = transformations or []
        self.index = index
        self.elementType = elementType

    def run(self):
        #TODO: Zest needs to distinguish data and params
        if self.method == "GET":
            prepare_r = requests.Request(self.method, self.url,
                headers=self.headers, params=self.data).prepare()
        else:
            _data = self.data
            if not isinstance(self.data, dict):
                _data = urlparse.parse_qs(self.data)
            prepare_r = requests.Request(self.method, self.url,
                headers=self.headers, data=_data).prepare()
        session = requests.session()
        resp = session.send(prepare_r)
        return self._run_assertions(resp)

    def _set_result(self, assert_type, passed, expectation=None, result=None, msg=None):
        if passed:
            return {"assert_type": assert_type, "passed": True}
        else:
            if msg:
                msg = msg.format(expectation=expectation, result=result)
            else:
                msg = "Expecting {expectation} but received {result} instead.".format(
                    expectation=expectation, result=result)
            return {"assert_type": assert_type, "passed": False, "msg": msg}

    def _run_assertions(self, resp):
        statement_report = {"url": self.url, "assertions": []}
        assertions = statement_report["assertions"]
        for assertion in self.assertions:
            if assertion["elementType"] == "ZestAssertStatusCode":
                assertions.append(self._assert_status_code(resp, assertion))
            elif assertion["elementType"] == "ZestAssertLength":
                assertions.append(self._assert_length(resp, assertion))
            elif assertion["elementType"] == "ZestAssertHeader":
                assertions.append(self._assert_header(resp, assertion))
            elif assertion["elementType"] == "ZestAssertBody":
                assertions.append(self._assert_body(resp, assertion))
        return statement_report

    def _assert_status_code(self, resp, assertion):
        if int(resp.status_code) != int(assertion["code"]):
            return self._set_result("ZestAssertStatusCode", False,
                expectation=assertion["code"], result=resp.status_code)
        else:
            return self._set_result("ZestAssertStatusCode", True)

    def _assert_length(self, resp, assertion):
        if resp.headers.get("transfer-encoding") == "chunked":
            return self._set_result("ZestAssertLength", False,
                msg="Expecting Content-Length in the header but response is sent with chunked transfer encoding.")
        else:
            content_length = resp.headers.get("content-length")
            if content_length:
                if int(content_length) == int(assertion["length"]):
                    return self._set_result("ZestAssertLength", True)
                else:
                    return self._set_result("ZestAssertLength", False,
                        expectation=assertion["length"],
                        result=content_length,
                        msg="Expecting content-length be {expectation} byte long but \
received {resukt} bytes instead.")
            else:
                return self._set_result("ZestAssertLength", False,
                    msg="Expecting Content-Length in the response header but there is none.")

    def _assert_header(self, resp, assertion):
        #TODO: need to dig down how to implement this with regex and conditional checks
        #      so, we now only allow assert EQUAL
        headers = filter(None, assertion["headers"].split("\r\n"))
        e_headers = {}
        for header in headers:
            name, value = header.split(":")
            e_headers[name.strip()] = value.strip()
        for name, value in e_headers.items():
            actual = resp.headers.get(name)
            if actual:
                if actual == value:
                    return self._set_result("ZestAssertHeader", True)
                else:
                    return self._set_result("ZestAssertHeader", False,
                        expectation="{h}: {ev}".format(h=name, ev=value),
                        result="{h}: {av}".format(h=name, av=actual))
            else:
                return self._set_result("ZestAssertHeader", False,
                    expectation="{h}: {ev}".format(h=name, ev=value),
                    result=name,
                    msg="Expecting {expectation} in the response header but there is none.")

    def _assert_body(self, resp, assertion):
        #TODO: similar to _assert_header, I am going to implement EQUAL only
        if "json" in resp.headers["content-type"]:
            actual = str(resp.json())
        else:
            actual = resp.text

        if actual == assertion["body"]:
            return self._set_result("ZestAssertBody", True)
        else:
            return self._set_result("ZestAssertBody", False, msg="Body does not match.")

    def to_dict(self):
        statement = dict(
            url = self.url,
            data = self.data,
            method = self.method,
            headers = self.headers,
            response = self.response,
            assertions = self.assertions,
            transformations = self.transformations,
            index = self.index,
            elementType = self.elementType
        )
        return statement

    def __str__(self):
        return str(self.to_dict())

    def __unicode__(self):
        return unicode(self.to_dict())

    def __repr__(self):
        return repr(self.to_dict())
