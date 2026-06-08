import type { Router } from 'vue-router'
import { beforeEach } from './global/beforeEach'
import { afterEach } from './global/afterEach'

export const setupRouterGuard = (router: Router): void => {
  router.beforeEach(beforeEach)
  router.afterEach(afterEach)
}