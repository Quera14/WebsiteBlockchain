import { createSignal, Index, onMount, type Component } from "solid-js";
import axios from "axios";

import "./App.scss";

const instance = axios.create({
  baseURL: "http://localhost:8000/blockchain",
});

interface IBlock {
  index: number;
  proof: number;
  data: string;
  timestamp: string;
  prev_hash: string;
  curr_hash: string;
  valid: boolean;
  // TODO: Add time how much time is needed to mine a block
}

const App: Component = () => {
  const [chains, setChains] = createSignal<IBlock[]>([]);
  const [blokchainType, setBlockchainType] = createSignal("sha256");

  return (
    <main>
      <h1>BLOCKCHAIN</h1>
      <select
        value={blokchainType()}
        onInput={async (e) => {
          setBlockchainType(e.currentTarget.value);
          const res = await instance.get(`/${blokchainType()}`);
          const chains = res.data.chain.map((data: any) => ({
            ...data,
            valid: true,
          }));
          setChains(chains);
        }}
      >
        <option value="sha256">sha256</option>
        <option value="keccak">keccak</option>
        <option value="skein">skein</option>
      </select>
      <div class="demo">
        <Index each={chains()}>
          {(item, index) => {
            return (
              <div
                class={item().valid ? "container valid" : "container not-valid"}
              >
                <div class="wrapper">
                  <p>Block:</p>
                  <div style="display: flex; align-items: center">
                    <div class="hashtag">#</div>
                    <div class="blockid" style="flex: 1">
                      {item().index}
                    </div>
                  </div>
                </div>
                <div class="wrapper">
                  <p>Nonce:</p>
                  <div class="blockid">{item().proof}</div>
                </div>
                <div class="wrapper" style="align-items: start">
                  <p>Data:</p>
                  <div class="dataid">
                    <textarea
                      name="data"
                      id="inputdata"
                      cols="30"
                      rows="10"
                      value={item().data}
                      onInput={(e) => {
                        const blockchain = [...chains()];
                        if (typeof e.data === "string") {
                          blockchain[index] = {
                            ...blockchain[index],
                            data: blockchain[index].data + e.data,
                            valid: false,
                          };
                        } else {
                          blockchain[index] = {
                            ...blockchain[index],
                            data: "",
                            valid: false,
                          };
                        }
                        for (let i = index + 1; i < blockchain.length; i++) {
                          blockchain[i] = {
                            ...blockchain[i],
                            valid: false,
                          };
                        }
                        setChains(blockchain);
                      }}
                    >
                      {item().data}
                    </textarea>
                  </div>
                </div>
                <div class="wrapper">
                  <p>prev:</p>
                  <div class="blockid">{item().prev_hash}</div>
                </div>
                <div class="wrapper">
                  <p>Hash:</p>
                  <div class="blockid">{item().curr_hash}</div>
                </div>
                <button
                  class="button"
                  onClick={async () => {
                    if (item().valid) {
                      return;
                    }
                    const res = await instance.post(
                      `/${blokchainType()}/mine/${item().index}`,
                      {
                        data: item().data,
                      }
                    );
                    setChains((prev) => {
                      const newChain = [...prev];
                      newChain[index] = {
                        ...res.data,
                        valid: true,
                      };
                      for (let i = index + 1; i < newChain.length; i++) {
                        newChain[i] = {
                          ...newChain[i],
                          valid: false,
                        };
                      }
                      return newChain;
                    });
                  }}
                >
                  Mine
                </button>
              </div>
            );
          }}
        </Index>
      </div>
    </main>
  );
};

export default App;
