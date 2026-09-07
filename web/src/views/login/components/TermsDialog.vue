<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
    modelValue: {
        type: Boolean,
        default: false,
    },
    agreed: {
        type: Boolean,
        default: false,
    },
})

const emit = defineEmits([
    'update:modelValue',
    'update:agreed',
    'confirm',
    'decline',
])

const localAgreed = ref(props.agreed)
const termsContentRef = ref<HTMLDivElement | null>(null)

// 监听外部 agreed 变化，同步本地复选框状态
watch(
    () => props.agreed,
    (newVal) => {
        localAgreed.value = newVal
    }
)

// 监听弹窗显示状态，打开时重置滚动位置
watch(
    () => props.modelValue,
    (visible) => {
        if (visible) {
            // 打开弹窗时，滚动到顶部
            nextTick(() => {
                if (termsContentRef.value) {
                    termsContentRef.value.scrollTop = 0
                }
            })
            // 如果外部已经同意，则同步本地状态
            if (props.agreed) {
                localAgreed.value = true
            }
        }
    }
)

// 处理弹窗关闭（通过点击 X、ESC、遮罩等）
function handleVisibleChange(visible: boolean) {
    if (!visible) {
        // 如果用户直接关闭弹窗，且尚未同意，则视为拒绝，但不发送 decline 事件（避免意外触发）
        // 实际上 el-dialog 关闭会触发 update:modelValue，我们只需要传递 visible
        emit('update:modelValue', visible)
    } else {
        emit('update:modelValue', visible)
    }
}

// 弹窗完全关闭后的回调
function handleClosed() {
    // 如果用户未同意就关闭了弹窗，不强制重置，但可以在这里清理状态
    // 这里什么都不做，交由父组件决定
}

// 复选框变化
function handleAgreeChange(checked: boolean) {
    // 更新父组件的 agreed 状态
    emit('update:agreed', checked)
}

// 点击“同意并关闭”
function handleConfirm() {
    if (!localAgreed.value) {
        ElMessage.warning('请先勾选同意条款')
        return
    }
    // 确保父组件 agreed 为 true
    emit('update:agreed', true)
    emit('confirm', true)
    // 关闭弹窗
    emit('update:modelValue', false)
}

// 点击“暂不同意”
function handleDecline() {
    // 如果之前已经同意过，点击暂不同意可能意味着撤销同意，视业务而定
    // 这里我们将其设为 false，并通知父组件
    localAgreed.value = false
    emit('update:agreed', false)
    emit('decline', false)
    // 关闭弹窗
    emit('update:modelValue', false)
}
</script>

<template>
    <el-dialog :model-value="modelValue" :title="'《OpenAdmin 服务条款》'" width="60%" :close-on-click-modal="false"
        :close-on-press-escape="true" :destroy-on-close="false" :align-center="true" class="terms-dialog"
        @update:model-value="handleVisibleChange" @closed="handleClosed">

        <template #default>
            <!-- 条款内容区域 -->
            <div class="terms-content" ref="termsContentRef">
                <!-- 第1条 -->
                <div class="terms-section">
                    <div class="section-title"><span class="num">1</span> 接受条款</div>
                    <p>欢迎使用 OpenAdmin 平台（以下简称"本平台"）。本平台由 OpenAdmin
                        技术团队开发并运营。通过注册、访问或使用本平台的任何服务，即表示您已阅读、理解并同意受本《注册用户条款》的约束。</p>
                    <p>如果您不同意本条款的任何部分，请勿注册或使用本平台的任何服务。本条款构成您与 OpenAdmin 之间具有法律约束力的协议。</p>
                    <div class="info-box">💡 <strong>提示：</strong>建议您在注册前完整阅读本条款，如有疑问可通过官方渠道咨询。</div>
                </div>

                <!-- 第2条 -->
                <div class="terms-section">
                    <div class="section-title"><span class="num">2</span> 服务描述</div>
                    <p>OpenAdmin 提供包括但不限于以下服务：</p>
                    <ul>
                        <li>数据可视化与仪表盘管理</li>
                        <li>用户权限与角色管理系统</li>
                        <li>API 接口管理与网关服务</li>
                        <li>实时日志监控与告警通知</li>
                        <li>文件存储与内容分发服务</li>
                        <li>团队协作与项目管理工具</li>
                    </ul>
                    <p>本平台保留随时修改、暂停或终止部分或全部服务的权利，无需事先通知用户，但将尽合理努力提前公告。</p>
                </div>

                <!-- 第3条 -->
                <div class="terms-section">
                    <div class="section-title"><span class="num">3</span> 账户注册与安全</div>
                    <p>3.1 用户注册时必须提供真实、准确、完整且最新的个人信息。</p>
                    <p>3.2 用户须年满 16 周岁方可注册使用本平台。</p>
                    <p>3.3 用户应对其账户下的所有活动承担全部责任。请妥善保管账户密码及访问凭证。</p>
                    <p>3.4 如发现任何未经授权使用账户的情况，用户应立即通知本平台。</p>
                </div>

                <!-- 第4条 -->
                <div class="terms-section">
                    <div class="section-title"><span class="num">4</span> 用户行为规范</div>
                    <p>用户承诺不得从事以下行为：</p>
                    <ul>
                        <li>违反中华人民共和国法律法规及社会公序良俗的行为</li>
                        <li>上传、发布、传输任何含有病毒、木马、恶意代码的内容</li>
                        <li>未经授权访问、干扰、破坏本平台的服务器、网络或其他系统</li>
                        <li>利用本平台从事任何欺诈、虚假宣传或侵犯他人权益的活动</li>
                        <li>未经许可收集、存储、使用其他用户的个人信息</li>
                        <li>对平台源代码进行逆向工程、反编译或以其他方式试图获取源代码</li>
                    </ul>
                    <div class="highlight-box">⚠️ <strong>注意：</strong>违反上述规范的用户，本平台有权立即终止其账户权限，并保留追究法律责任的权利。</div>
                </div>

                <!-- 第5条 -->
                <div class="terms-section">
                    <div class="section-title"><span class="num">5</span> 知识产权</div>
                    <p>5.1 本平台的所有内容归 OpenAdmin 或其授权方所有，受相关知识产权法律保护。</p>
                    <p>5.2 用户在使用本平台服务过程中产生的原创内容，其知识产权归用户所有。</p>
                    <p>5.3 未经本平台书面许可，用户不得复制、修改、传播、出售或利用本平台的任何内容用于商业目的。</p>
                </div>

                <!-- 第6条 -->
                <div class="terms-section">
                    <div class="section-title"><span class="num">6</span> 隐私与数据保护</div>
                    <p>6.1 本平台重视用户隐私保护，详情请参阅《隐私政策》。</p>
                    <p>6.2 本平台采用行业标准的安全措施保护用户数据。</p>
                    <p>6.3 用户同意本平台在法律法规要求或维护平台权益等情况下使用或披露其信息。</p>
                </div>

                <!-- 第7条 -->
                <div class="terms-section">
                    <div class="section-title"><span class="num">7</span> 服务费用与变更</div>
                    <p>7.1 本平台提供免费与付费两种服务模式，具体费用标准以平台公示为准。</p>
                    <p>7.2 本平台有权根据运营需要调整服务费用，将至少提前 15 日通知用户。</p>
                </div>

                <!-- 第8条 -->
                <div class="terms-section">
                    <div class="section-title"><span class="num">8</span> 免责声明</div>
                    <p>8.1 本平台按"现状"和"可用"状态提供服务，不对服务的可靠性、准确性、完整性做出保证。</p>
                    <p>8.2 因不可抗力、基础网络故障、用户操作不当等原因导致的服务中断，本平台不承担责任。</p>
                </div>

                <!-- 第9条 -->
                <div class="terms-section">
                    <div class="section-title"><span class="num">9</span> 服务终止</div>
                    <p>9.1 用户可以随时申请注销账户。</p>
                    <p>9.2 如用户违反本条款，本平台有权暂停或终止用户的账户访问权限。</p>
                </div>

                <!-- 第10条 -->
                <div class="terms-section">
                    <div class="section-title"><span class="num">10</span> 条款修改</div>
                    <p>10.1 本平台保留随时修改本条款的权利，修改后的条款将在平台公示。</p>
                    <p>10.2 用户继续使用本平台服务即视为接受修改后的条款。</p>
                </div>

                <!-- 第11条 -->
                <div class="terms-section">
                    <div class="section-title"><span class="num">11</span> 法律适用与争议解决</div>
                    <p>11.1 本条款适用中华人民共和国法律。</p>
                    <p>11.2 因本条款引起的争议，双方应首先通过友好协商解决。协商不成的，可向有管辖权的人民法院提起诉讼。</p>
                </div>

                <!-- 第12条 -->
                <div class="terms-section">
                    <div class="section-title"><span class="num">12</span> 联系我们</div>
                    <ul>
                        <li>📧 电子邮箱：<strong>legal@openadmin.io</strong></li>
                        <li>📞 客服热线：<strong>400-888-0000</strong>（工作日 9:00-18:00）</li>
                    </ul>
                </div>
            </div>
        </template>

        <!-- 弹窗底部操作区 -->
        <template #footer>
            <div class="dialog-footer">
                <div class="agree-wrapper">
                    <el-checkbox v-model="localAgreed" @change="handleAgreeChange">
                        <span class="agree-label">
                            我已完整阅读并同意条款的全部内容。
                        </span>
                    </el-checkbox>
                </div>
                <div class="action-buttons">
                    <el-button type="primary" :disabled="!localAgreed" @click="handleConfirm">
                        同意并关闭
                    </el-button>
                    <el-button @click="handleDecline">暂不同意</el-button>
                </div>
            </div>
        </template>
    </el-dialog>
</template>

<style scoped>
/* ==================== 弹窗样式 ==================== */
/* 弹窗整体：约束不超过视口，溢出隐藏由内部条款区接管滚动 */
.terms-dialog :deep(.el-dialog) {
    max-height: 90vh;
    overflow: hidden;
}

.terms-dialog :deep(.el-dialog__body) {
    padding: 20px 24px;
    overflow: hidden;
}

/* 条款内容区：直接设置高度上限，扣除 header/footer/边距后剩余空间，超出则内部滚动 */
.terms-content {
    padding-right: 4px;
    max-height: calc(90vh - 180px);
    overflow-y: auto;
    padding: 20px;
    border-radius: 8px;
}

.terms-section {
    margin-bottom: 22px;
}

.terms-section:last-child {
    margin-bottom: 0;
}

.section-title {
    font-size: 15px;
    font-weight: 700;
    color: var(--el-text-color-primary);
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 8px;
    letter-spacing: -0.2px;
}

.section-title .num {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 24px;
    height: 24px;
    background: var(--el-color-primary-light-9);
    color: var(--el-color-primary);
    border-radius: 6px;
    font-size: 12px;
    font-weight: 700;
    flex-shrink: 0;
}

.terms-section p {
    font-size: 13px;
    color: var(--el-text-color-regular);
    margin-bottom: 8px;
    line-height: 1.6;
}

.terms-section ul {
    list-style: none;
    padding-left: 32px;
    margin-bottom: 8px;
}

.terms-section ul li {
    font-size: 13px;
    color: var(--el-text-color-regular);
    margin-bottom: 6px;
    position: relative;
    padding-left: 16px;
    line-height: 1.6;
}

.terms-section ul li::before {
    content: '';
    position: absolute;
    left: 0;
    top: 9px;
    width: 5px;
    height: 5px;
    background: var(--el-color-primary);
    border-radius: 50%;
    opacity: 0.6;
}

.highlight-box {
    background: #fff8f0;
    border-left: 4px solid #ff6b35;
    padding: 10px 14px;
    border-radius: 0 8px 8px 0;
    margin: 10px 0;
    font-size: 12px;
    color: #6b4a2b;
    line-height: 1.6;
}

.info-box {
    background: var(--el-color-primary-light-9);
    border-left: 4px solid var(--el-color-primary);
    padding: 10px 14px;
    border-radius: 0 8px 8px 0;
    margin: 10px 0;
    font-size: 12px;
    color: #3a4a9f;
    line-height: 1.6;
}

/* 弹窗底部 */
.dialog-footer {
    display: flex;
    flex-direction: column;
    gap: 14px;
    padding-top: 4px;
}

.agree-wrapper {
    display: flex;
    align-items: flex-start;
}

.agree-label {
    font-size: 13px;
    color: var(--el-text-color-regular);
    line-height: 1.6;
}

.action-buttons {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
}

/* ==================== 响应式 ==================== */
@media (max-width: 768px) {
    .terms-dialog :deep(.el-dialog) {
        width: 95% !important;
        max-height: 90vh;
        margin: 5vh auto !important;
    }

    .terms-dialog :deep(.el-dialog__body) {
        padding: 16px;
    }

    .terms-content {
        max-height: calc(90vh - 200px);
    }

    .action-buttons {
        flex-direction: column-reverse;
        gap: 8px;
    }

    .action-buttons .el-button {
        width: 100%;
        margin: 0;
    }
}
</style>