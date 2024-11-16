import type { HardhatUserConfig } from "hardhat/config";
import '@openzeppelin/hardhat-upgrades'
import "@nomicfoundation/hardhat-toolbox-viem";

import * as dotenv from 'dotenv'
dotenv.config()
const ZERO_PRIVATE_KEY ='0x0000000000000000000000000000000000000000000000000000000000000000'
const MAINNET_PRIVATE_KEY = process.env.MAINNET_PRIVATE_KEY ?? ZERO_PRIVATE_KEY
const TESTNET_PRIVATE_KEY = process.env.TESTNET_PRIVATE_KEY ??  ZERO_PRIVATE_KEY

const config: HardhatUserConfig = {
  networks: {
    testnet: {
      chainId: 31337,
        url: 'http://localhost:8545/',
	accounts: [TESTNET_PRIVATE_KEY]
      }
  },
  solidity: {
    compilers: [
      {
        version: '0.7.0',
        settings: {
          optimizer: {
            enabled: true,
            runs: 200
          }
        }
      },
      {
        version: '0.8.27'
      },
      {
        version: '0.8.19',
	settings: {
          optimizer: {
            enabled: true,
            runs: 200
          }
        }
      }
    ]
  },
  typechain: {
    outDir: "typechain",
    target: "ethers-v6",
  }
};

export default config;
