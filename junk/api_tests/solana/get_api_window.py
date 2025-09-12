import PySimpleGUI as sg
from solana_rpc_client import Client
from abstract_gui import *
import inspect
from variables import *
client = Client()
def convert_to_lower(string_obj):
    return ''.join([f"_{char.lower()}" if char in list('ABCDEFGHIJKLMNOPQRSTUVWXYZ') else char for char in str(string_obj)])
def convert_to_upper(string_obj):
    return ''.join([f"{string[1][0].upper()}{string[1][1:].lower()}" if string[1] and string[0] > 0 else string[1] for string in enumerate(string_obj.split('_'))])
def convert_to_body(string_obj):
    return f"_{convert_to_lower(string_obj)}_body"
def get_functions_js():
    return {'get_balance': ['pubkey', 'commitment'], 'get_account_info': ['pubkey', 'commitment', 'encoding', 'data_slice'], 'get_account_info_json_parsed': ['pubkey', 'commitment'], 'get_block_commitment': ['slot'], 'get_block_time': ['slot'], 'get_cluster_nodes': [], 'get_block': ['slot', 'encoding', 'max_supported_transaction_version', 'None'], 'get_recent_performance_samples': ['limit'], 'get_block_height': ['commitment'], 'get_blocks': ['start_slot', 'end_slot'], 'get_signatures_for_address': ['account', 'before', 'until', 'limit', 'commitment'], 'get_transaction': ['signature', 'encoding', 'commitment', 'max_supported_transaction_version'], 'get_epoch_info': ['commitment'], 'get_epoch_schedule': [], 'get_fee_for_message': ['message', 'commitment'], 'get_first_available_block': [], 'get_genesis_hash': [], 'get_identity': [], 'get_inflation_governor': ['commitment'], 'get_inflation_rate': [], 'get_inflation_reward': ['pubkeys', 'epoch', 'commitment'], 'get_largest_accounts': ['filter_opt', 'commitment'], 'get_leader_schedule': ['epoch', 'commitment'], 'get_minimum_balance_for_rent_exemption': ['usize', 'commitment'], 'get_multiple_accounts': ['pubkeys', 'commitment', 'encoding', 'data_slice'], 'get_multiple_accounts_json_parsed': ['pubkeys', 'commitment'], 'get_program_accounts': ['pubkey', 'commitment', 'encoding', 'data_slice', 'filters', 'types.MemcmpOpts'], 'get_program_accounts_json_parsed': ['pubkey', 'commitment', 'filters', 'types.MemcmpOpts'], 'get_latest_blockhash': ['commitment'], 'get_signature_statuses': ['signatures', 'search_transaction_history'], 'get_slot': ['commitment'], 'get_slot_leader': ['commitment'], 'get_stake_activation': ['pubkey', 'epoch', 'commitment'], 'get_supply': ['commitment'], 'get_token_account_balance': ['pubkey', 'commitment'], 'get_token_accounts_by_delegate': ['delegate', 'opts', 'commitment'], 'get_token_accounts_by_delegate_json_parsed': ['delegate', 'opts', 'commitment'], 'get_token_accounts_by_owner': ['owner', 'opts', 'commitment'], 'get_token_accounts_by_owner_json_parsed': ['owner', 'opts', 'commitment'], 'get_token_largest_accounts': ['pubkey', 'commitment'], 'get_token_supply': ['pubkey', 'commitment'], 'get_transaction_count': ['commitment'], 'get_minimum_ledger_slot': [], 'get_version': [], 'get_vote_accounts': ['commitment'], 'request_airdrop': ['pubkey', 'lamports', 'commitment'], 'send_raw_transaction': ['txn', 'opts'], 'send_transaction': ['txn', 'Transaction', '*signers', 'opts', 'recent_blockhash'], 'simulate_transaction': ['txn', 'VersionedTransaction', 'sig_verify', 'commitment'], 'validator_exit': [], '__post_send_with_confirm': ['resp', 'conf_comm', 'last_valid_block_height'], 'confirm_transaction': ['tx_sig', 'commitment', 'sleep_seconds', 'last_valid_block_height']}
def get_functions_list():
    return list(get_functions_js().keys())
def get_list_vars():
    return list(get_functions_js().values())
def get_all_vars():
    list_obj=[]
    for obj in get_list_vars():
        list_obj +=obj
    return list_obj
def get_vars(function):
    return get_functions_js().get(function)
def get_longest(list_obj):
    list_obj = [len(string) for string in list_obj]
    list_obj.sort()
    return list_obj[-1]
def get_var_inputs():
    inputs=[]
    for i in range(get_longest(get_list_vars())):
        inputs.append([make_component('Input','',size=(get_longest(get_all_vars()),1),key=f'var_{i}'),make_component('Input','',size=(get_longest(get_all_vars()),1),key=f'input_{i}')])
    return [inputs]
def clear_inputs(window):
    for i in range(get_longest(get_list_vars())):
        [window[f'{string}_{i}'].update(value='') for string in ['var','input']]
def get_dict_from_vars(values, function):
    sig = inspect.signature(function)
    filtered_values = {key: get_sample_var(key) for key in list(sig.parameters.keys()) if key in values}
    return filtered_values
def get_result(function,values):
    try:
        result = function(**values)
    except TypeError as e:
        print(f"Error calling function: {e}")
        result = {}
    return result
def get_function(string_obj):
    try:
        function = getattr(client, convert_to_lower(string_obj))
    except TypeError as e:
        print(f"Error calling function: {e}")
        function =None
    return function
def get_body_function(string_obj):
    try:
        function = getattr(client, convert_to_body(string_obj))
    except TypeError as e:
        print(f"Error calling function: {e}")
        function =None
    return function
def get_all_rpc_bodies():
    results={}
    for lowered in get_functions_list():
        if lowered:
            function = get_function(lowered)
            if function:
                sig = inspect.signature(function)
                dictsa = {}
                revsa = {}
                for i,var in enumerate(list(sig.parameters.keys())):
                    dictsa[var]=get_sample_var(var)
                    revsa[get_sample_var(var)]:var
                    # Get function by its name dynamically
                try:
                    print(revsa)
                    # Pass filtered arguments
                    result = get_result(function,dictsa)
                    params =result.get('params',[])
                    
                    for i,param in enumerate(params):
                        if isinstance(param,dict):
                            for key,value in param.items():
                                param[key]=key
                            params[i]= param
                        else:
                            for key,value in dictsa.items():
                                if value == param:
                                    param = key
                                    params[i] = key
                                    break
                except TypeError as e:
                    print(f"Error calling function: {e}")
                    result = {}
                results[lowered] = result
    return results
def second_window():
    sg.theme('DarkGrey14')
    menu_def = [['&File', ['&Open     Ctrl-O', '&Save       Ctrl-S', '&Properties', 'E&xit']],
                ['&Edit', ['&Paste', ['Special', 'Normal', ], 'Undo', 'Options::this_is_a_menu_key'], ],
                ['&Toolbar', ['---', 'Command &1', 'Command &2','---', 'Command &3', 'Command &4']],
                ['&NetworkTools', ['---','RPC',['Add RPC', 'Choose RPC','get Manual RPC'], 'Choose RPC &2','---', 'Command &3', 'Command &4']],
                ['APIs',['chainScan'],
                ['&Help', ['&About...']]]]
    right_click_menu = ['Unused', ['Right', '!&Click', '&Menu', 'E&xit', 'Properties']]
    layout = [[sg.Menu(menu_def, tearoff=True, font='_ 12', key='-MENUBAR-')],
              [sg.ButtonMenu('ButtonMenu', right_click_menu, key='-BMENU-', text_color='red', disabled_text_color='green'),
               sg.Button('Plain Button')],
              make_component('Frame','url',[[sg.Input('https://solcatcher.io', size=(40, 1), key='url')]]),
              make_component('combo', get_functions_list(), size=(get_longest(get_functions_list()), 1), key='body_functions',enable_events=True),
              make_component('combo', [convert_to_upper(string) for string in get_functions_list()],size=(get_longest(get_functions_list()), 1), key='call_functions',enable_events=True)],get_var_inputs(),[sg.Multiline(size=(88, 20), font='Courier 10', key='output')]

    window = sg.Window('Script launcher', layout)
    results = {}
    while True:
        event, values = window.read()
        if event == 'EXIT' or event == sg.WIN_CLOSED:
            break  # exit button clicked
        if event in ['body_functions', 'call_functions']:
            clear_inputs(window)
            lowered = convert_to_lower(values['body_functions'])
            window['body_functions'].update(value=lowered)
            window['call_functions'].update(value=get_sample_var(lowered))
            if lowered:
                function =get_body_function(lowered)
                sig = inspect.signature(function)
                dictsa = {}
                for i,var in enumerate(list(sig.parameters.keys())):
                    window[f'var_{i}'].update(value=var)
                    window[f'input_{i}'].update(value=get_sample_var(var))
                    dictsa[var]=get_sample_var(var)
                try:
                    
                    
                    # Pass filtered arguments
                    result = get_result(function,dictsa)
                    print(result)
                    window['output'].update(result)
                except TypeError as e:
                    print(f"Error calling function: {e}")
                    result = {}
                results[lowered] = results
                


second_window()
