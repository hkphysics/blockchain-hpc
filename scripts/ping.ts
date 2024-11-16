// deploy upgradeable client

import { ethers, upgrades } from 'hardhat'

async function main (): void {
    const [owner] = await ethers.getSigners()
    const contractAddress = process.env.EXAMPLE_CONTRACT
    const name = 'HpcExample'
    const HpcExample = await ethers.getContractFactory(name)
    const hpcExample = HpcExample.attach(contractAddress)
    const tokenAddress = await hpcExample.getToken()
    console.log(tokenAddress)
    const HpcToken = await ethers.getContractFactory('HpcToken')
    const hpcToken = HpcToken.attach(tokenAddress)
    const tokens = console.log(
        await hpcToken.balanceOf(owner)
    )
    const fee = BigInt("10000000000000000")
    const tx1 = await hpcToken.approve(contractAddress, fee)
    const tx = await hpcExample.doTransferAndRequest(
	"ping",
	"{}",
	"",
	"cbor",
	"10000000000000000000",
	fee
    )
    await tx.wait()
}

// We recommend this pattern to be able to use async/await everywhere
// and properly handle errors.
main().catch((error) => {
  console.error(error)
  process.exitCode = 1
})
