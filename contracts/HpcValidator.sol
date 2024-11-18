//SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "./interface/IHpcValidator.sol";

contract HpcValidator is IHpcValidator {
    function fulfillOracleRequest2AndRefund(
        bytes32,
	uint256,
	address,
	bytes4,
	uint256,
	bytes calldata,
	uint256
    ) external pure returns (bool) {
	return true;
    }
}
