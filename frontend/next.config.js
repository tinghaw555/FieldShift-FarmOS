/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  basePath: '/FieldShift-FarmOS',
  images: {
    unoptimized: true,
  },
  reactStrictMode: true,
  swcMinify: true,
  trailingSlash: true,
}

module.exports = nextConfig
