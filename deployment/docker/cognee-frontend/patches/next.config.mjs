/** @type {import('next').NextConfig} */
const nextConfig = {
    // CozyCognee Patch: 通过环境变量控制开发指示器（devIndicators）
    // 隐藏左下角的开发工具指示器
    // 设置 NEXT_DISABLE_DEV_INDICATORS=true 来禁用 devIndicators
    // 注意：Next.js 本身不支持通过环境变量控制 devIndicators，这里通过补丁实现
    devIndicators: process.env.NEXT_DISABLE_DEV_INDICATORS === 'true' ? false : undefined,
    
    // 保留原有的 env 配置（如果需要）
    env: {
        NEXT_PUBLIC_BACKEND_API_URL: process.env.NEXT_PUBLIC_BACKEND_API_URL,
        NEXT_PUBLIC_MCP_API_URL: process.env.NEXT_PUBLIC_MCP_API_URL,
        NEXT_PUBLIC_COGWIT_API_KEY: process.env.NEXT_PUBLIC_COGWIT_API_KEY,
        NEXT_PUBLIC_IS_CLOUD_ENVIRONMENT: process.env.NEXT_PUBLIC_IS_CLOUD_ENVIRONMENT,
    },
};

export default nextConfig;
