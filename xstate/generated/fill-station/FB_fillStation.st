(* GENERATED from fillStation.machine.ts - do not edit by hand. Regenerate: npm run export *)

TYPE E_FillStation_State :
(
    idle := 0,
    running_filling := 1,
    running_heating := 2,
    running_settling := 3,
    running_draining := 4,
    fault := 5,
    lockedOut := 6,
    emergency := 7
);
END_TYPE

FUNCTION_BLOCK FB_FillStation
VAR_INPUT
    evSTART : BOOL; (* one-scan pulse *)
    evESTOP : BOOL; (* one-scan pulse *)
    evLEVEL_HIGH : BOOL; (* one-scan pulse *)
    evSTOP : BOOL; (* one-scan pulse *)
    evTEMP_OK : BOOL; (* one-scan pulse *)
    evLEVEL_LOW : BOOL; (* one-scan pulse *)
    evRESET : BOOL; (* one-scan pulse *)
    evMAINT_RESET : BOOL; (* one-scan pulse *)
    evESTOP_RELEASE : BOOL; (* one-scan pulse *)
END_VAR
VAR_OUTPUT
    State : E_FillStation_State := E_FillStation_State.idle;
    INLET : BOOL;
    HEATER : BOOL;
    OUTLET : BOOL;
END_VAR
VAR
    retries : DINT := 0;
    lastFault : STRING(32) := '';
    NextState : E_FillStation_State;
    tState : TON;
END_VAR

(* state timer: ET = time spent in current state *)
tState(IN := TRUE, PT := T#24D);
NextState := State;

CASE State OF
    E_FillStation_State.idle:
        IF evSTART THEN
            NextState := E_FillStation_State.running_filling;
        ELSIF evESTOP THEN (* inherited from fillStation *)
            NextState := E_FillStation_State.emergency;
        END_IF;
    E_FillStation_State.running_filling:
        IF evLEVEL_HIGH THEN
            NextState := E_FillStation_State.running_heating;
        ELSIF tState.ET >= T#30000MS (* after FILL_TIMEOUT *) THEN
            A_setFault(code := 'FILL_TIMEOUT');
            NextState := E_FillStation_State.fault;
        ELSIF evSTOP THEN (* inherited from fillStation.running *)
            NextState := E_FillStation_State.idle;
        ELSIF evESTOP THEN (* inherited from fillStation *)
            NextState := E_FillStation_State.emergency;
        END_IF;
    E_FillStation_State.running_heating:
        IF evTEMP_OK THEN
            NextState := E_FillStation_State.running_settling;
        ELSIF tState.ET >= T#60000MS (* after HEAT_TIMEOUT *) THEN
            A_setFault(code := 'HEAT_TIMEOUT');
            NextState := E_FillStation_State.fault;
        ELSIF evSTOP THEN (* inherited from fillStation.running *)
            NextState := E_FillStation_State.idle;
        ELSIF evESTOP THEN (* inherited from fillStation *)
            NextState := E_FillStation_State.emergency;
        END_IF;
    E_FillStation_State.running_settling:
        IF tState.ET >= T#5000MS (* after SETTLE_TIME *) THEN
            NextState := E_FillStation_State.running_draining;
        ELSIF evSTOP THEN (* inherited from fillStation.running *)
            NextState := E_FillStation_State.idle;
        ELSIF evESTOP THEN (* inherited from fillStation *)
            NextState := E_FillStation_State.emergency;
        END_IF;
    E_FillStation_State.running_draining:
        IF evLEVEL_LOW THEN
            NextState := E_FillStation_State.idle;
        ELSIF evSTOP THEN (* inherited from fillStation.running *)
            NextState := E_FillStation_State.idle;
        ELSIF evESTOP THEN (* inherited from fillStation *)
            NextState := E_FillStation_State.emergency;
        END_IF;
    E_FillStation_State.fault:
        IF evRESET AND G_canRetry() THEN
            A_countRetry();
            NextState := E_FillStation_State.idle;
        ELSIF evRESET THEN
            NextState := E_FillStation_State.lockedOut;
        ELSIF evESTOP THEN (* inherited from fillStation *)
            NextState := E_FillStation_State.emergency;
        END_IF;
    E_FillStation_State.lockedOut:
        IF evMAINT_RESET THEN
            A_clearFaults();
            NextState := E_FillStation_State.idle;
        ELSIF evESTOP THEN (* inherited from fillStation *)
            NextState := E_FillStation_State.emergency;
        END_IF;
    E_FillStation_State.emergency:
        IF evESTOP_RELEASE THEN
            NextState := E_FillStation_State.idle;
        ELSIF evESTOP THEN (* inherited from fillStation *)
            NextState := E_FillStation_State.emergency;
        END_IF;
END_CASE;

IF NextState <> State THEN
    State := NextState;
    tState(IN := FALSE); (* restart timer on state change *)
END_IF;

(* consume event pulses *)
evSTART := FALSE;
evESTOP := FALSE;
evLEVEL_HIGH := FALSE;
evSTOP := FALSE;
evTEMP_OK := FALSE;
evLEVEL_LOW := FALSE;
evRESET := FALSE;
evMAINT_RESET := FALSE;
evESTOP_RELEASE := FALSE;

(* Moore outputs from tags *)
INLET := (State = E_FillStation_State.running_filling);
HEATER := (State = E_FillStation_State.running_heating);
OUTLET := (State = E_FillStation_State.running_draining);

END_FUNCTION_BLOCK

METHOD G_canRetry : BOOL
(* TS source:
({context})=>context.retries<MAX_RETRIES
*)
G_canRetry := FALSE; (* TODO *)
END_METHOD

METHOD A_setFault
VAR_INPUT
    code : STRING;
END_VAR
(* TS source:
lastFault := (_,params)=>params.code
*)
; (* TODO *)
END_METHOD

METHOD A_countRetry
(* TS source:
retries := ({context})=>context.retries+1
*)
; (* TODO *)
END_METHOD

METHOD A_clearFaults
(* TS source:
retries := 0
lastFault := null
*)
; (* TODO *)
END_METHOD
