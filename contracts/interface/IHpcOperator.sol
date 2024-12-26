// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "@chainlink/contracts/src/v0.8/interfaces/OperatorInterface.sol";
interface IHpcOperator is OperatorInterface {
    function fulfillOracleRequest2AndRefund(
        bytes32,
    uint256,
    address,
    bytes4,
    uint256,
    bytes calldata,
    uint256
  ) external returns (bool);
}