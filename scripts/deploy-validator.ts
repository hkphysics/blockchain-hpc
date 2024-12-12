import { ethers, upgrades } from 'hardhat'

async function main (): void {
  const HpcValidator = await ethers.getContractFactory('HpcValidator')
  const hpcValidator =
        await upgrades.deployProxy(
          HpcValidator
        )

  await hpcValidator.waitForDeployment()
  console.log(`validator deployed to ${await hpcValidator.getAddress()}`)
}

// We recommend this pattern to be able to use async/await everywhere
// and properly handle errors.
main().catch((error) => {
  console.error(error)
  process.exitCode = 1
})
