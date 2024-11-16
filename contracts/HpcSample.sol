// SPDX-License-Identifier: MIT
pragma solidity ^0.8.15;
import "@openzeppelin/contracts/utils/Strings.sol";
import "@chainlink/contracts/src/v0.8/ChainlinkClient.sol";
import "@chainlink/contracts/src/v0.8/shared/access/ConfirmedOwner.sol";

contract HpcSample is ChainlinkClient, ConfirmedOwner {
    using Chainlink for Chainlink.Request;
    bytes public result;
    mapping(bytes32 => bytes) public results;
    address public oracleId;
    string public jobId;
    uint256 public fee;

    constructor(address oracleId_, string memory jobId_,
                uint256 fee_,
		address token_) ConfirmedOwner(msg.sender) {
	_setChainlinkToken(token_);
        oracleId = oracleId_;
        jobId = jobId_;
        fee = fee_;
    }

    function doRequest(
        string memory service_,
        string memory data_,
        string memory keypath_,
        string memory abi_,
        string memory multiplier_) public returns (bytes32 requestId) {
          Chainlink.Request memory req = _buildChainlinkRequest(
            bytes32(bytes(jobId)),
            address(this), this.fulfillBytes.selector);
        req._add("service", service_);
        req._add("data", data_);
        req._add("keypath", keypath_);
        req._add("abi", abi_);
        req._add("multiplier", multiplier_);
        return _sendChainlinkRequestTo(oracleId, req, fee);
    }

    function doTransferAndRequest(
        string memory service_,
        string memory data_,
        string memory keypath_,
        string memory abi_,
        string memory multiplier_,
        uint256 fee_) public returns (bytes32 requestId) {
        require(LinkTokenInterface(getToken()).transferFrom(
               msg.sender, address(this), fee_), 'transfer failed');
        Chainlink.Request memory req = _buildChainlinkRequest(
            bytes32(bytes(jobId)),
            address(this), this.fulfillBytes.selector);
        req._add("service", service_);
        req._add("data", data_);
        req._add("keypath", keypath_);
        req._add("abi", abi_);
        req._add("multiplier", multiplier_);
        req._add("refundTo",
                Strings.toHexString(uint160(msg.sender), 20));
        return _sendChainlinkRequestTo(oracleId, req, fee_);
    }

    function fulfillBytes(bytes32 _requestId, bytes memory bytesData)
        public recordChainlinkFulfillment(_requestId) {
        result = bytesData;
        results[_requestId] = bytesData;
    }


    function changeOracle(address _oracle) public onlyOwner {
        oracleId = _oracle;
    }

    function changeJobId(string memory _jobId) public onlyOwner {
        jobId = _jobId;
    }

    function changeFee(uint256 _fee) public onlyOwner {
        fee = _fee;
    }

    function changeToken(address _address) public onlyOwner {
        _setChainlinkToken(_address);
    }

    function getToken() public view returns (address) {
        return _chainlinkTokenAddress();
    }

    function withdrawLink() public onlyOwner {
        LinkTokenInterface link = LinkTokenInterface(_chainlinkTokenAddress());
            require(link.transfer(msg.sender, link.balanceOf(address(this))), "Unable to transfer");
  }
    /** Use a function like this if you want to process the item
        as int256 */

    function getInt256(bytes32 _requestId) public view returns (int256) {
       return toInt256(results[_requestId]);
    }

    function toInt256(bytes memory _bytes) internal pure
      returns (int256 value) {
          assembly {
            value := mload(add(_bytes, 0x20))
      }
   }

}
