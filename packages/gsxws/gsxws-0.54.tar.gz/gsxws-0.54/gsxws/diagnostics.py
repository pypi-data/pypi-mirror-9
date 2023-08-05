# -*- coding: utf-8 -*-

from core import GsxObject, GsxError


class Diagnostics(GsxObject):
    _namespace = "glob:"

    def initiate(self):
        """
        The Initiate iOS Diagnostic API allows users to initiate Diagnostic Request for iOS Device.
        Then it sends the diagnostic URL (diags://<Ticket Number >) as an email or SMS 
        to the email address or phone number based on the information provided in the request. 
        The ticket is generated within GSX system.
        """
        self._submit("initiateRequestData", "InitiateIOSDiagnostic",
                     "initiateResponseData")

        return self._req.objects.ticketNumber

    def fetch(self):
        """
        The Fetch Repair Diagnostics API allows the service providers/depot/carriers
        to fetch MRI/CPU diagnostic details from the Apple Diagnostic Repository OR
        diagnostic test details of iOS Devices.
        The ticket is generated within GSX system.

        >>> Diagnostics(diagnosticEventNumber='12942008007242012052919').fetch()
        """
        if hasattr(self, "alternateDeviceId"):
            self._submit("lookupRequestData", "FetchIOSDiagnostic",
                         "lookupResponseData")
        else:
            self._submit("lookupRequestData", "FetchRepairDiagnostic",
                         "FetchRepairDiagnosticResponse")

        return self._req.objects

    def events(self):
        """
        The Fetch Diagnostic Event Numbers API allows users to retrieve all
        diagnostic event numbers associated with provided input
        (serial number or alternate device ID).
        """
        self._submit("lookupRequestData", "FetchDiagnosticEventNumbers",
                     "diagnosticEventNumbers")
        return self._req.objects
