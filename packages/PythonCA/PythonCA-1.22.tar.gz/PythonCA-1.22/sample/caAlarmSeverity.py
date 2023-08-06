
class AlarmSeverity:
    NO_ALARM  =0x0
    MINOR_ALARM=0x1
    MAJOR_ALARM=0x2
    INVALID_ALARM=0x3
    ALARM_NSEV=INVALID_ALARM+1
    Strings=(
	"NO_ALARM",
	"MINOR",
	"MAJOR",
	"INVALID",
        )
    Colors=(
        "green","yellow","red","grey")
class AlarmStatus:
    NO_ALARM = 0
    READ_ALARM = 1
    WRITE_ALARM = 2
    #/* ANALOG ALARMS */
    HIHI_ALARM = 3
    HIGH_ALARM = 4
    LOLO_ALARM = 5
    LOW_ALARM = 6
    #/* BINARY ALARMS */
    STATE_ALARM = 7
    COS_ALARM = 8
    #/* other alarms */
    COMM_ALARM = 9
    TIMEOUT_ALARM = 10
    HW_LIMIT_ALARM = 11
    CALC_ALARM = 12
    SCAN_ALARM = 13
    LINK_ALARM = 14
    SOFT_ALARM = 15
    BAD_SUB_ALARM = 16
    UDF_ALARM = 17
    DISABLE_ALARM = 18
    SIMM_ALARM = 19
    READ_ACCESS_ALARM = 20
    WRITE_ACCESS_ALARM = 21
    Strings=(
        "NO_ALARM",
        "READ",
        "WRITE",
        "HIHI",
        "HIGH",
        "LOLO",
        "LOW",
        "STATE",
        "COS",
        "COMM",
        "TIMEOUT",
        "HWLIMIT",
        "CALC",
        "SCAN",
        "LINK",
        "SOFT",
        "BAD_SUB",
        "UDF",
        "DISABLE",
        "SIMM",
        "READ_ACCESS",
        "WRITE_ACCESS",
        )
