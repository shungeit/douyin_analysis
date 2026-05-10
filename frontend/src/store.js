import { reactive } from 'vue'

export const store = reactive({
  user: null,
  setUser(user) {
    this.user = user
  },
  clearUser() {
    this.user = null
  },
})
