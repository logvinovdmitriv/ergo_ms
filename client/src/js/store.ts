// client/src/store/index.ts
import { createStore } from 'vuex'

export interface RootState {
  profile: any | null
  organizations: any[]
}

const store = createStore<RootState>({
  state: () => ({
    profile: null,
    organizations: [],
  }),
  mutations: {
    setProfile(state, payload) { state.profile = payload },
    setOrganizations(state, list) { state.organizations = list || [] },
  },
  actions: {},
  getters: {
    isAuthenticated: (state) => !!state.profile,
  },
})

export default store
