// deploy upgradeable client

import { ethers, upgrades } from 'hardhat'

async function main (): void {
    const [owner,  feeCollector, operator] = await ethers.getSigners();
    const OPERATOR_HPC = process.env.OPERATOR_HPC
    const NODE_ETH_ADDRESS = process.env.NODE_ETH_ADDRESS
    const name = 'HpcOperator'
    const HpcOperator = await ethers.getContractFactory(name)
    const hpcOperator = HpcOperator.attach(OPERATOR_HPC)
    const tx0 = await hpcOperator.setAuthorizedSenders([ NODE_ETH_ADDRESS ])
    console.log(NODE_ETH_ADDRESS)
    await tx0.wait()
    const tx1 = await owner.sendTransaction({
      to: NODE_ETH_ADDRESS,
      value: ethers.parseEther("10.0"), // Sends exactly 1.0 ether
    });
    await tx1.wait()
    const Token = await ethers.getContractFactory('HpcToken')
    const token = Token.attach(await hpcOperator.getChainlinkToken())
    await token.grantMintAndBurnRoles(owner)
    await token.mint(owner, BigInt("100000000000000000000000"))
    console.log(`${name} deployed to ${await token.getAddress()}`)
}

// We recommend this pattern to be able to use async/await everywhere
// and properly handle errors.
main().catch((error) => {
  console.error(error)
  process.exitCode = 1
})
