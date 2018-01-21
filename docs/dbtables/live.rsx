
.. csv-table:: [Autogenerated table scheme of table "live] Rolling database for (raw) incoming observations."
    :header: "Field", "Type", "Null", "Key", "Default", "Extra"

    "statnr","int(11)","NO","MUL","None",""
    "datum","int(8)","NO","MUL","None",""
    "datumsec","int(11)","NO","MUL","None",""
    "stdmin","smallint(4)","NO","","None",""
    "msgtyp","enum('na','bufr','synop')","YES","","na",""
    "stint","enum('na','essential','additional')","YES","","na",""
    "utime","timestamp","NO","MUL","CURRENT_TIMESTAMP",""
    "ucount","tinyint(3) unsigned","YES","","0",""
    "...","...","...","...","...","..."



* Non-unique key named *bufr_statnr* on ``(statnr)``
* Non-unique key named *bufr_datumsec* on ``(datumsec)``
* Non-unique key named *bufr_datum* on ``(datum)``
* Non-unique key named *bufr_einspiel* on ``(utime)``
* **Unique-key** named *bufr_statnr_datumsec_msgtyp* on ``(statnr, datumsec, msgtyp)``


