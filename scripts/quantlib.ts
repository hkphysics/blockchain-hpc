// deploy upgradeable client

import { ethers, upgrades } from 'hardhat'
import  fixed_rate_bond_request from './fixed_rate_bond_request.json'

async function main (): void {
    const [owner] = await ethers.getSigners()
    const cid = await hre.ipfs.putDag(fixed_rate_bond_request)
    const contractAddress = process.env.EXAMPLE_CONTRACT
    const name = 'HpcExample'
    const HpcExample = await ethers.getContractFactory(name)
    const hpcExample = HpcExample.attach(contractAddress)
    const tokenAddress = await hpcExample.getToken()
    console.log(cid.toString())
    console.log(tokenAddress)
    const HpcToken = await ethers.getContractFactory('HpcToken')
    const hpcToken = HpcToken.attach(tokenAddress)
    const tokens = console.log(
        await hpcToken.balanceOf(owner)
    )
    const fee = BigInt("10000000000000000")
    const tx1 = await hpcToken.approve(contractAddress, fee)
/*
    const tx = await hpcExample.doTransferAndRequest(
	"ipfs",
	"cid:" + cid.toString(),
	"",
	"cbor",
	"10000000000000000000",
	fee
    )
    await tx.wait()
    */
}

// We recommend this pattern to be able to use async/await everywhere
// and properly handle errors.
main().catch((error) => {
  console.error(error)
  process.exitCode = 1
})
