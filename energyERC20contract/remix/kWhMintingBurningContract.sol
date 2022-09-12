// SPDX-License-Identifier: GPL-3.0

pragma solidity ^0.5.0;

import "@openzeppelin/contracts@2.5/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts@2.5/token/ERC20/ERC20Detailed.sol";
import "@openzeppelin/contracts@2.5/token/ERC20/ERC20Mintable.sol";
import "@openzeppelin/contracts@2.5/token/ERC20/ERC20Burnable.sol";

/**
 * @title SampleERC20
 * @dev Create a sample ERC20 standard token
 */
contract KWHMintingBurningERC20 is ERC20,ERC20Detailed,ERC20Mintable,ERC20Burnable {

    uint256 public initialSupply = 1000000;

    constructor() ERC20Detailed("KiloWattHour","KWH",3) public {
        _mint(msg.sender, initialSupply);
    }
}