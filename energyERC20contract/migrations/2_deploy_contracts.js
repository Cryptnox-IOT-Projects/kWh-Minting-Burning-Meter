var KWHContract = artifacts.require("../contracts/KWHContract.sol");

module.exports = function(deployer, network, accounts) {
    deployer.deploy(KWHContract, {from: accounts[0]});
   };