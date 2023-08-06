SMPP
====

SMPP Transport
^^^^^^^^^^^^^^

.. py:module:: vumi.transports.smpp

.. autoclass:: SmppTransport


Example configuration
^^^^^^^^^^^^^^^^^^^^^

::

    system_id: <provided by SMSC>
    password: <provided by SMSC>
    host: smpp.smppgateway.com
    port: 2775
    system_type: <provided by SMSC>

    # Optional variables, some SMSCs require these to be set.
    interface_version: "34"
    dest_addr_ton: 1
    dest_addr_npi: 1
    registered_delivery: 1

    TRANSPORT_NAME: smpp_transport

    # Number Recognition
    COUNTRY_CODE: "27"

    OPERATOR_NUMBER:
        VODACOM: "<outbound MSISDN to be used for this MNO>"
        MTN: "<outbound MSISDN to be used for this MNO>"
        CELLC: "<outbound MSISDN to be used for this MNO>"
        VIRGIN: "<outbound MSISDN to be used for this MNO>"
        8TA: "<outbound MSISDN to be used for this MNO>"
        UNKNOWN: "<outbound MSISDN to be used for this MNO>"

    OPERATOR_PREFIX:
        2771:
            27710: MTN
            27711: VODACOM
            27712: VODACOM
            27713: VODACOM
            27714: VODACOM
            27715: VODACOM
            27716: VODACOM
            27717: MTN
            27719: MTN

        2772: VODACOM
        2773: MTN
        2774:
            27740: CELLC
            27741: VIRGIN
            27742: CELLC
            27743: CELLC
            27744: CELLC
            27745: CELLC
            27746: CELLC
            27747: CELLC
            27748: CELLC
            27749: CELLC

        2776: VODACOM
        2778: MTN
        2779: VODACOM
        2781:
            27811: 8TA
            27812: 8TA
            27813: 8TA
            27814: 8TA

        2782: VODACOM
        2783: MTN
        2784: CELLC

Notes
^^^^^

* This transport does no MSISDN normalization
* This transport tries to guess the outbound MSISDN for any SMS sent
  using a operator prefix lookup.

Use of Redis in the SMPP Transport
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Redis is used for all situations where temporary information must be
cached where:

    a. it will survive system shutdowns
    b. it can be shared between workers

One use of Redis is for mapping between SMPP sequence_numbers and long
term unique id's on the ESME and the SMSC.

The sequence_number parameter is a revolving set of integers used to
pair outgoing async pdu's with their response, i.e. submit_sm &
submit_sm_resp.

Both submit_sm and the corresponding submit_sm_resp will share a
single sequence_number, however, for long term storage and future
reference, it is necessary to link the id of the message stored on the
SMSC (message_id in the submit_sm_resp) back to the id of the sent
message.  As the submit_sm_resp pdu's are received, the original id is
looked up in Redis via the sequence_number and associated with the
message_id in the response.

Followup pdu's from the SMSC (i.e. delivery reports) will reference
the original message by the message_id held by the SMSC which was
returned in the submit_sm_resp.
