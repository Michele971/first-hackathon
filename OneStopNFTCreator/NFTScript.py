import hashlib
import json

import algosdk
from algosdk.v2client import algod
from beaker import sandbox


def mintNFT(algod_client, creator_address, creator_private_key, asset_name, asset_unit_name):
    # Get the creator's account information
    creator_account_info = algod_client.account_info(creator_address)
    creator_account_public_key = creator_account_info['address']
    creator_account_seq_num = creator_account_info['sequence']

    # Create the asset creation transaction
    params = algod_client.suggested_params()
    txn = algosdk.future.transaction.AssetConfigTxn(
        sender=creator_account_public_key,
        sp=params,
        total=1,  # Only one of this NFT will be created
        default_frozen=False,  # Allow the asset to be transferred
        unit_name=asset_unit_name,
        asset_name=asset_name,
        manager=creator_address,  # Creator has all permissions
        reserve=None,
        freeze=None,
        clawback=None,
        url=None,
        metadata_hash=None,
    )

    # Sign the transaction with the creator's private key
    signed_txn = txn.sign(creator_private_key)

    # Send the transaction
    algod_client.send_transaction(signed_txn)

    # Wait for the transaction to be confirmed
    confirmed_txn = None
    while confirmed_txn is None:
        try:
            txn_id = signed_txn.transaction.get_txid()
            confirmed_txn = algod_client.pending_transaction_info(txn_id)
        except Exception:
            pass

    # Get the asset ID from the confirmed transaction
    asset_id = confirmed_txn['asset-config-transaction']['asset-id']

    return asset_id

    return 0  #your confirmed transaction's asset id should be returned instead


def transferNFT(algod_client, creator_address, creator_private_key, receiver_address, receiver_private_key, asset_id):
    # Get the creator's account information
    creator_account_info = algod_client.account_info(creator_address)
    creator_account_public_key = creator_account_info['address']
    creator_account_seq_num = creator_account_info['sequence']

    # Get the receiver's account information
    receiver_account_info = algod_client.account_info(receiver_address)
    receiver_account_public_key = receiver_account_info['address']
    receiver_account_seq_num = receiver_account_info['sequence']

    # Create a transaction to transfer the NFT
    params = algod_client.suggested_params()
    txn = algosdk.future.transaction.AssetTransferTxn(
        creator_address=creator_account_public_key,
        recipient_address=receiver_account_public_key,
        close_assets_to=creator_address,
        asset_id=asset_id,
        amount=1,
        params=params,
    )

    # Sign the transaction with the creator's private key
    signed_txn = txn.sign(creator_private_key)

    # Send the transaction
    algod_client.send_transaction(signed_txn)

    # Wait for the transaction to be confirmed
    confirmed_txn = None
    while confirmed_txn is None:
        try:
            txn_id = signed_txn.transaction.get_txid()
            confirmed_txn = algod_client.pending_transaction_info(txn_id)
        except Exception:
            pass

    # Sign the transaction with the receiver's private key to close out any remaining assets
    close_txn = algosdk.future.transaction.AssetTransferTxn(
        creator_address=receiver_account_public_key,
        recipient_address=creator_account_public_key,
        close_assets_to=receiver_address,
        asset_id=asset_id,
        amount=0,
        params=params,
    ).sign(receiver_private_key)

    # Send the close transaction
    algod_client.send_transaction(close_txn)

    return confirmed_txn['asset-transfer-transaction']['asset-id']
