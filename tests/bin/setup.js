if( !web3.eth.accounts ) {
    personal.newAccount( "" );
}
var main = web3.eth.accounts[0];
miner.setEtherbase( main );
miner.start();
personal.unlockAccount( main, "" );
