const viewStore = {
  state: {
    visSidePanelActive: true,
  },
  getters: {},
  mutations: {
    setVisShowSideBar(state, show) {
      state.visSidePanelActive = show;
    },
  },
  actions: {},
};
export default viewStore;
