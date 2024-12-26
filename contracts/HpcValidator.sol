//SPDX-License-Identifier: MIT
import "./vendor/ConfirmedOwnerUpgradeable.sol";

pragma solidity ^0.8.0;

import "./interface/IHpcValidator.sol";
import "./interface/IHpcOperator.sol";

contract HpcValidator is IHpcValidator, ConfirmedOwnerUpgradeable {
    bool private initialized;
    IHpcOperator internal operator;
    function initialize(address operator_, address owner_) public {
        __ConfirmedOwnerUpgradeable_init(owner_, address(0));
	operator = IHpcOperator(operator_);
    }
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
