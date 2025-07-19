function createToken(
    address _underlying_token,
    string memory name,
    string memory symbol
) public onlyRole(CREATOR_ROLE) returns (address) {
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
