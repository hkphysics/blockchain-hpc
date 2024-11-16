// SPDX-License-Identifier: MIT
pragma solidity ^0.8.15;
import "./HpcClient.sol";
import "@openzeppelin/contracts/utils/Strings.sol";
import "@openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@chainlink/contracts/src/v0.8/interfaces/OperatorInterface.sol";


contract HpcExample is Initializable, OwnableUpgradeable, HpcClient {
    using Chainlink for Chainlink.Request;
    bytes public result;
    mapping(bytes32 => bytes) public results;
    address public oracleId;
    string public jobId;
    uint256 public fee;

    function initialize(
      address oracleId_,
      string memory jobId_,
      uint256 fee_,
      address token_) public initializer {
        __Ownable_init();
        __HpcClient_init();
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

    function getChainlinkToken() public view returns (address) {
        return getToken();
    }

    function withdrawLink() public onlyOwner {
        LinkTokenInterface link = LinkTokenInterface(_chainlinkTokenAddress());
            require(link.transfer(msg.sender, link.balanceOf(address(this))), "Unable to transfer");
    }

    function typeAndVersion() external pure virtual returns (string memory) {
        return "HPC 0.2";
    }

    // do not allow renouncing ownership
    function renounceOwnership() public view override onlyOwner {
    }
}
