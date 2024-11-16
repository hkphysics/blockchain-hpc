// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
import {BurnMintERC677} from "@chainlink/contracts/src/v0.8/shared/token/ERC677/BurnMintERC677.sol";

contract HpcToken is BurnMintERC677 {
  constructor() BurnMintERC677("Hpc Token", "HPC", 18, 1e27) {}
}
