export const resources = {
    users: {
        label: "用户管理",
        columns: [
            { key: 'id', label: 'ID' },
            { key: 'username', label: '用户名' },
            { key: 'email', label: '邮箱' },
            { key: 'role', label: '角色' },
            { key: 'created_at', label: '注册时间' }
        ],
        fields: [
            { name: 'username', label: '用户名', type: 'text', required: true },
            { name: 'email', label: '邮箱', type: 'email', required: true },
            { name: 'role', label: '角色', type: 'select', options: ['user', 'admin'] },
            { name: 'bio', label: '简介', type: 'textarea' },
            { name: 'location', label: '位置', type: 'text' }
        ]
    },
    trips: {
        label: "旅行管理",
        columns: [
            { key: 'id', label: 'ID' },
            { key: 'name', label: '名称' },
            { key: 'creator_id', label: '创建者ID' },
            { key: 'start_date', label: '开始日期' },
            { key: 'status', label: '状态' },
            { key: 'visibility', label: '可见性' }
        ],
        fields: [
            { name: 'name', label: '名称', type: 'text', required: true },
            { name: 'description', label: '描述', type: 'textarea' },
            { name: 'start_date', label: '开始日期', type: 'date', required: true },
            { name: 'end_date', label: '结束日期', type: 'date', required: true },
            { name: 'status', label: '状态', type: 'select', options: ['planning', 'ongoing', 'completed', 'cancelled'] },
            { name: 'visibility', label: '可见性', type: 'select', options: ['public', 'private'] },
            { name: 'budget_amount', label: '预算', type: 'number' }
        ]
    },
    posts: {
        label: "帖子管理",
        columns: [
            { key: 'id', label: 'ID' },
            { key: 'title', label: '标题' },
            { key: 'author_id', label: '作者ID' },
            { key: 'created_at', label: '创建时间' }
        ],
        fields: [
            { name: 'title', label: '标题', type: 'text', required: true },
            { name: 'text', label: '内容', type: 'textarea', required: true },
            { name: 'visibility', label: '可见性', type: 'select', options: ['public', 'private', 'followers'] }
        ]
    },
    comments: {
        label: "评论管理",
        columns: [
            { key: 'id', label: 'ID' },
            { key: 'content', label: '内容' },
            { key: 'author_id', label: '作者ID' },
            { key: 'post_id', label: '帖子ID' }
        ],
        fields: [
            { name: 'content', label: '内容', type: 'textarea', required: true }
        ]
    },
    likes: {
        label: "点赞管理",
        columns: [
            { key: 'id', label: 'ID' },
            { key: 'user_id', label: '用户ID' },
            { key: 'post_id', label: '帖子ID' }
        ],
        fields: []
    },
    conversations: {
        label: "会话管理",
        columns: [
            { key: 'id', label: 'ID' },
            { key: 'title', label: '标题' },
            { key: 'conversation_type', label: '类型' }
        ],
        fields: [
            { name: 'title', label: '标题', type: 'text' }
        ]
    },
    messages: {
        label: "消息管理",
        columns: [
            { key: 'id', label: 'ID' },
            { key: 'content_text', label: '内容' },
            { key: 'sender_id', label: '发送者ID' },
            { key: 'sent_at', label: '发送时间' }
        ],
        fields: [
            { name: 'content_text', label: '内容', type: 'textarea', required: true }
        ]
    },
    activities: {
        label: "活动管理",
        columns: [
            { key: 'id', label: 'ID' },
            { key: 'title', label: '标题' },
            { key: 'trip_day_id', label: '日程ID' }
        ],
        fields: [
            { name: 'title', label: '标题', type: 'text', required: true },
            { name: 'description', label: '描述', type: 'textarea' },
            { name: 'start_time', label: '开始时间', type: 'datetime-local' },
            { name: 'end_time', label: '结束时间', type: 'datetime-local' }
        ]
    },
    transits: {
        label: "交通管理",
        columns: [
            { key: 'id', label: 'ID' },
            { key: 'type', label: '类型' },
            { key: 'trip_day_id', label: '日程ID' }
        ],
        fields: [
            { name: 'type', label: '类型', type: 'text', required: true },
            { name: 'start_time', label: '出发时间', type: 'datetime-local' },
            { name: 'end_time', label: '到达时间', type: 'datetime-local' }
        ]
    },
    trip_days: {
        label: "日程管理",
        columns: [
            { key: 'id', label: 'ID' },
            { key: 'day_index', label: '第几天' },
            { key: 'trip_id', label: '旅行ID' }
        ],
        fields: [
            { name: 'date', label: '日期', type: 'date' },
            { name: 'notes', label: '备注', type: 'textarea' }
        ]
    },
    trip_members: {
        label: "成员管理",
        columns: [
            { key: 'id', label: 'ID' },
            { key: 'trip_id', label: '旅行ID' },
            { key: 'user_id', label: '用户ID' },
            { key: 'role', label: '角色' }
        ],
        fields: [
            { name: 'role', label: '角色', type: 'select', options: ['owner', 'admin', 'member', 'viewer'] },
            { name: 'nickname', label: '昵称', type: 'text' }
        ]
    },
    post_images: {
        label: "帖子图片",
        columns: [
            { key: 'id', label: 'ID' },
            { key: 'post_id', label: '帖子ID' },
            { key: 'image_url', label: 'URL' }
        ],
        fields: [
            { name: 'image_url', label: 'URL', type: 'text', required: true },
            { name: 'display_order', label: '顺序', type: 'number' }
        ]
    },
    post_tags: {
        label: "帖子标签",
        columns: [
            { key: 'id', label: 'ID' },
            { key: 'post_id', label: '帖子ID' },
            { key: 'tag', label: '标签' }
        ],
        fields: [
            { name: 'tag', label: '标签', type: 'text', required: true }
        ]
    }
};
