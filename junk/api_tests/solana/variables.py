def sample_examples():
    signatures = ["5EzaJ7GrBUqT9gAGqNR1vNcduhpgc5agiLXWMW9hcmo4Lzbyqy66VFqa26uY81BkqWLtrpWr4NqkKvfRL5qzAfAt","2LLrwwzk3E8yb7JPwp8E15ZvYwnKHVHs1K9CNs6rzDiDUsCCU6U15UjAfMijur2bVK7Q7tvMC6p1J1xe3xjx8Gnn"]
    pubkey = "BJ8aUaWmAbbUdFFYhFbmhNPrH4NncWj7ACZD5E4bpump"
    mint = "HpfiQovafVvvKPgFMbYhbrY2LX9GeuTTR4saN25Xpump"
    account="GBzQG2iFrPwXjGtCnwNt9S5eHd8xAR8jUMt3QDJpnjud"
    delegate="TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
    signer = "HMU77m6WSL9Xew9YvVCgz1hLuhzamz74eD9avi4XPdr"
    slot = 287731841
    owner = "AfQ1oaudsGjvznX4JNEw671hi57JfWo4CWqhtkdgoVHU"
    return signatures,pubkey,mint,account,delegate,signer,slot,owner
def get_sample_var(var):
    signatures,pubkey,mint,account,delegate,signer,slot,owner = sample_examples()
    return {
     'tx':"01b3795ccfaac3eee838bb05c3b8284122c18acedcd645c914fe8e178c3b62640d8616d061cc818b26cab8ecf3855ecc",
     'mint':mint,
     'pubkeys': [pubkey, pubkey],
     'limit': 100,
     'recent_blockhash': "HZ5VGgojr2ZS3sFc7QUaiLGdzLmEGP7nHu5ZRhhoFjg4",
     'pubkey': pubkey,
     'start_slot': 287731841,
     'filters': [{'dataSize': 165}],
     'sig_verify': True,
     'Transaction': None,  # Placeholder if not using a specific transaction object yet
     'commitment': 'confirmed',
     'until': None,  # Can be user-input for upper range of transaction signature
     'before': None,  # Can be user-input for lower range of transaction signature
     '*signers': [],  # List of required signers
     'delegate': delegate,
     'opts': {'skipPreflight': True, 'preflightCommitment': 'confirmed'},
     'message': None,  # Message to be signed, if applicable
     'sleep_seconds': 2,
     'epoch': None,  # Epoch can be retrieved or user-specified
     'lamports': 0,  # Number of lamports for sending transactions
     'VersionedTransaction': None,  # Placeholder if using versioned transactions
     'signature': signatures[0],
     'search_transaction_history': True,
     'last_valid_block_height': 5000000,
     'txn': None,  # Placeholder for raw transaction data
     'filter_opt': {'mint': mint},  # Optional filter for mint
     'tx_sig': signatures[0],
     'encoding': "jsonParsed",
     'end_slot': slot,
     'account': account,
     'usize': 1024,
     'conf_comm': None,  # Placeholder for confirmation commitment
     'data_slice': {'offset': 0, 'bytes': 'base58_encoded_value'},
     'max_supported_transaction_version': 0,
     'owner': owner,
     'types.MemcmpOpts': 0,#{'offset': 0, 'bytes': 'base58_encoded_value'},
     'before': None,
     'signatures': [signatures[0], signatures[1]],
     'slot': slot,
     'signers':[signer,signer],
     'signer':signer,
     "preflight_commitment":True,
    }.get(var)
