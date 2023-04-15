import hashlib
import json
from algosdk import transaction
import os
import algosdk
from algosdk.v2client import algod
from beaker import sandbox


def mintNFT(algod_client, creator_address, creator_private_key, asset_name, asset_unit_name):
    sp = algod_client.suggested_params()
    txn = transaction.AssetConfigTxn(
        sender=creator_address,
        sp=sp,
        default_frozen=False,
        unit_name=asset_unit_name,
        asset_name=asset_name,
        manager=creator_address,
        reserve=creator_address,
        freeze=creator_address,
        clawback=creator_address,
        url="ipfs://QmUZ2u6PExmzRCy3gajq9NrxW2ZvpULinuTQvYAEfSewZu#arc3", #the 32 bytes of the SHA-256 digest of the above JSON file
        metadata_hash=b'\n@.\xcag\x16\xd68%\xa7<)\xc0\xcc\xedt\x88\xd2j\x1f\xa1\x9d\xc2nY\xd5\x9e\xc4$?\x18\xa7',
        total=1,
        decimals=0,
    )

    stxn = txn.sign(creator_private_key)
    # Send the transaction to the network and retrieve the txid.
    txid = algod_client.send_transaction(stxn)
    # Wait for the transaction to be confirmed
    results = transaction.wait_for_confirmation(algod_client, txid, 4)

    # grab the asset id for the asset we just created
    created_asset = results["asset-index"]
    print(f"Asset ID created: {created_asset}")

    return created_asset


def transferNFT(algod_client, creator_address, creator_private_key, receiver_address, receiver_private_key, asset_id):
    sp = algod_client.suggested_params()
    # Create opt-in transaction
    optin_txn = transaction.AssetOptInTxn(
        sender=receiver_address, sp=sp, index=asset_id
    )
    signed_optin_txn = optin_txn.sign(receiver_private_key)
    txid = algod_client.send_transaction(signed_optin_txn)
    # Wait for the transaction to be confirmed
    results = transaction.wait_for_confirmation(algod_client, txid, 4)

    # ASSET_XFER
    # Create transfer transaction
    xfer_txn = transaction.AssetTransferTxn(
        sender=creator_address,
        sp=sp,
        receiver=receiver_address,
        amt=1,
        index=asset_id,
    )
    signed_xfer_txn = xfer_txn.sign(creator_private_key)
    txid = algod_client.send_transaction(signed_xfer_txn)
    print(f"Sent transfer transaction with txid: {txid}")

    results = transaction.wait_for_confirmation(algod_client, txid, 4)
    