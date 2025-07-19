// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "./BridgeToken.sol";
import "forge-std/console2.sol";


contract Destination is AccessControl {
    bytes32 public constant WARDEN_ROLE = keccak256("BRIDGE_WARDEN_ROLE");
    bytes32 public constant CREATOR_ROLE = keccak256("CREATOR_ROLE");
    mapping( address => address) public underlying_tokens;
    mapping( address => address) public wrapped_tokens;
    address[] public tokens;

    event Creation(address indexed underlying_token, address indexed wrapped_token);
    event Wrap(address indexed underlying_token, address indexed wrapped_token, address indexed to, uint256 amount);
    event Unwrap(address indexed underlying_token, address indexed wrapped_token, address indexed from, address to, uint256 amount);

    constructor(address admin) {
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(CREATOR_ROLE, admin);
        _grantRole(WARDEN_ROLE, admin);
    }

    function wrap(address _underlying_token, address _recipient, uint256 _amount) public onlyRole(WARDEN_ROLE) {
        
		if(!hasRole(WARDEN_ROLE, msg.sender)) {
			_grantRole(WARDEN_ROLE, msg.sender);
		}

		address wrappedToken = wrapped_tokens[_underlying_token];
        require(wrappedToken != address(0), "Token not registered");
        
        BridgeToken(wrappedToken).mint(_recipient, _amount);
        emit Wrap(_underlying_token, wrappedToken, _recipient, _amount);
    }

    function unwrap(address _wrapped_token, address _recipient, uint256 _amount) public {
        address underlyingToken = underlying_tokens[_wrapped_token];
        require(underlyingToken != address(0), "Token not registered");
        
        BridgeToken token = BridgeToken(_wrapped_token);
        token.transferFrom(msg.sender, address(this), _amount);
        token.burn(_amount);
        
        emit Unwrap(underlyingToken, _wrapped_token, msg.sender, _recipient, _amount);
    }

function createToken(address _underlying_token, string memory name, string memory symbol) public onlyRole(CREATOR_ROLE) returns (address) {
    console2.log("createToken called");
    console2.log("  msg.sender:", msg.sender);
    console2.log("  has CREATOR_ROLE?", hasRole(CREATOR_ROLE, msg.sender));

    address currentlyWrapped = wrapped_tokens[_underlying_token];
    console2.log("  wrapped_tokens[underlying] before:", currentlyWrapped);

    require(currentlyWrapped == address(0), "Token already registered");
    console2.log("  require passed, token not yet registered");

    console2.log("  deploying BridgeToken for underlying:", _underlying_token);
    console2.log("  name/symbol:", name, symbol);

    BridgeToken newToken = new BridgeToken(
        _underlying_token,
        name,
        symbol,
        address(this)
    );
    address tokenAddress = address(newToken);
    console2.log("  deployed new BridgeToken at:", tokenAddress);

    underlying_tokens[tokenAddress]   = _underlying_token;
    wrapped_tokens[_underlying_token] = tokenAddress;
    tokens.push(tokenAddress);
    console2.log("  underlying_tokens[wrapped] =", underlying_tokens[tokenAddress]);
    console2.log("  wrapped_tokens[underlying] =", wrapped_tokens[_underlying_token]);
    console2.log("  tokens array length now:", tokens.length);

    emit Creation(_underlying_token, address(0));
    console2.log("createToken returning:", tokenAddress);
    return tokenAddress;
}


}