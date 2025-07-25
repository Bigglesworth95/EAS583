// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";

contract Source is AccessControl {
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant WARDEN_ROLE = keccak256("BRIDGE_WARDEN_ROLE");
	mapping( address => bool) public approved;
	address[] public tokens;

	event Deposit( address indexed token, address indexed recipient, uint256 amount );
	event Withdrawal( address indexed token, address indexed recipient, uint256 amount );
	event Registration( address indexed token );

    constructor( address admin ) {
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(ADMIN_ROLE, admin);
        _grantRole(WARDEN_ROLE, admin);

    }

	function deposit(address _token, address _recipient, uint256 _amount ) public {
		//Check if token being depoisted has been registered
		require(approved[_token]);
		//Use transferFrom to pull the tokens into the deposit contract
		ERC20(_token).transferFrom(msg.sender, address(this), _amount);
		//Emit a deposit event so that the bridge operator knows to make the necessary actions
		//on the destination side
		emit Deposit(_token, _recipient, _amount);
	}

	function withdraw(address _token, address _recipient, uint256 _amount ) onlyRole(WARDEN_ROLE) public {
		//check if function is being called by the contract owner
		require(msg.sender == _recipient);

		//push the tokens to the recipient using the ERC20 transfer function
		ERC20(_token).transfer(_recipient, _amount);

		//emit a withdraw event
		emit Withdrawal(_token, _recipient, _amount);
	}

	function registerToken(address _token) onlyRole(ADMIN_ROLE) public {
		//check that function is being called by the contract owner

		//check that token has not already been registered
		require(!approved[_token]);

		//add to registered tokens
		approved[_token] = true;

		//emit registration event
		emit Registration(_token);


	}


}
