import api from './index'

export interface LoginParams {
  username: string
  password: string
}

export interface RegisterParams {
  username: string
  email: string
  password: string
}

export interface TokenResponse {
  access: string
  refresh: string
}

export interface UserProfile {
  id: number
  username: string
  email: string
}

export const authApi = {
  login: (data: LoginParams) => api.post<TokenResponse>('/auth/login/', data),
  register: (data: RegisterParams) => api.post<TokenResponse>('/auth/register/', data),
  refresh: (refresh: string) =>
    api.post<TokenResponse>('/auth/refresh/', { refresh }),
  logout: (refresh: string) => api.post<void>('/auth/logout/', { refresh }),
  me: () => api.get<UserProfile>('/auth/me/'),
}
