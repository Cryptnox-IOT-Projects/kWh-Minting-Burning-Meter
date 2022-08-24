pragma solidity ^0.5.0;

import "../node_modules/openzeppelin-solidity/contracts/token/ERC20/ERC20.sol";
import "../node_modules/openzeppelin-solidity/contracts/token/ERC20/ERC20Mintable.sol";
import "../node_modules/openzeppelin-solidity/contracts/token/ERC20/ERC20Burnable.sol";
import "../node_modules/openzeppelin-solidity/contracts/token/ERC20/ERC20Detailed.sol";


contract KWHContract is ERC20,ERC20Detailed,ERC20Mintable,ERC20Burnable {

uint256 public initialSupply = 1000000;

constructor() ERC20Detailed("KiloWattHour","KWH",3) public {
  _mint(msg.sender, initialSupply);
    }

}