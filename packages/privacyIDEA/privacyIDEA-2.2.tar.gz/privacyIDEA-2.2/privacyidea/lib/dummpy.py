
def get_options(machine_id=None,
                token_id=None,
                application=None,
                machinetoken_id=None):
    """
    returns a dictionary of the options for a given tuple
    of machine, token and application from the table
    MachineTokenOptions.

    :param machine_id: id of the machine
    :param token_id: id ot the token
    :param application: name of the application
    :param machinetoken_id: id of the machineToken-entry

    :return: option dictionary

    You either need to specify (machine_ind, token_id, application) or
    the machinetoken_id.
    """
    options = {}
    if machinetoken_id:
        sqlquery = Session.query(MachineTokenOptions).\
            filter(MachineTokenOptions.machinetoken_id == machinetoken_id)
        for option in sqlquery:
            options[option.mt_key] = option.mt_value
    elif (machine_id and token_id and application):
        raise NotImplementedError("the tuple machine_id, token_id, "
                                  "application is not implemented, yet.")
    else:
        raise Exception("You either need to specify the machinetoken_id"
                        "or the tuple token_id, machine_id, application.")
    return options





#
#   Attach options
#

