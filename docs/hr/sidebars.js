// @ts-check

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  useCasesSidebar: [{ type: 'autogenerated', dirName: 'use_cases' }],

  tutorialSidebar: [
    {
      type: 'doc',
      label: 'Welcome',
      id: 'docs/intro',
    },
    {
      type: 'category',
      label: 'Get started',
      collapsed: true,
      collapsible: true,
      items: [
        'docs/get_started/installation',
        'docs/get_started/configuration',
        'docs/get_started/environment',
        'docs/get_started/hello_world',
      ],
      link: {
        type: 'doc',
        id: 'docs/get_started/first_steps',
      },
    },
    {
      type: 'category',
      label: 'Core API',
      link: {
        type: 'doc',
        id: 'docs/core_api/intro',
      },
      items: [
        'docs/core_api/connect',
        'docs/core_api/apply',
        'docs/core_api/execute',
      ]
    },
    {
      type: 'category',
      label: 'Connect API',
      link: {
        type: 'doc',
        id: 'docs/connect_api/overview',
      },
      items: [
      ]
      
    },
    {
      type: 'category',
      label: 'Apply API',
      link: {
        type: 'doc',
        id: 'docs/apply_api/component',
      },
      items: [
        'docs/apply_api/model',
        'docs/apply_api/listener',
        'docs/apply_api/vector_index',
        'docs/apply_api/stack',
        'docs/apply_api/datatype',
        'docs/apply_api/schema',
        'docs/apply_api/table',
        'docs/apply_api/dataset',
        'docs/apply_api/metric',
        'docs/apply_api/validation',
        'docs/apply_api/trainer',
      ]
    },
    {
      type: 'category',
      label: 'Execute API',
      link: {
        type: 'doc',
        id: 'docs/execute_api/overview',
      },
      items: [
        {
          type: 'category',
          label: 'Inserting data',
          link: {
            type: 'doc',
            id: 'docs/execute_api/inserting_data',
          },
          items: [
            'docs/execute_api/data_encodings_and_schemas',
            'docs/execute_api/basic_insertion',
            'docs/execute_api/encoding_special_data_types',
            'docs/execute_api/using_hybrid_storage_to_handle_large_data_blobs',
            'docs/execute_api/referring_to_data_from_diverse_sources',
          ]
        },
        {
          type: 'category',
          label: 'Selecting data',
          link: {
            type: 'doc',
            id: 'docs/execute_api/select_queries',
          },
          items: [
            'docs/execute_api/mongodb_queries',
            'docs/execute_api/sql_queries',
          ]
        },
        {
          type: 'category',
          label: 'Vector search',
          link: {
            type: 'doc',
            id: 'docs/execute_api/vector_search',
          },
          items: [
            'docs/execute_api/setting_up_vector_search',
            'docs/execute_api/vector_search_queries',
            'docs/execute_api/native_vector_search',
            'docs/execute_api/sidecar_index_vector_search',
          ]
        },
        'docs/execute_api/update_queries',
        'docs/execute_api/delete_queries',
        'docs/execute_api/predictions',
      ]
    },
    {
      type: 'category',
      label: 'Models',
      link: {
        type: 'doc',
        id: 'docs/models/overview',
      },
      items: [
        'docs/models/key_methods',
        'docs/models/daemonizing_models_with_listeners',
        'docs/models/linking_interdependent_models',
        'docs/models/training_models',
        'docs/models/evaluating_models',
        'docs/models/llms',
        'docs/models/embeddings',
        'docs/models/bring_your_own_models',
      ]
    },
    {
      type: 'category',
      label: 'Reusable snippets',
      collapsed: true,
      collapsible: true,
      items: [
        'docs/reusable_snippets/connect_to_superduperdb',
        'docs/reusable_snippets/create_datatype',
        'docs/reusable_snippets/get_useful_sample_data',
        'docs/reusable_snippets/insert_data',
        'docs/reusable_snippets/compute_features',
        'docs/reusable_snippets/build_text_embedding_model',
        'docs/reusable_snippets/build_image_embedding_model',
        'docs/reusable_snippets/build_multimodal_embedding_models',
        'docs/reusable_snippets/build_llm',
        'docs/reusable_snippets/create_vector_index',
        'docs/reusable_snippets/perform_a_vector_search',
        'docs/reusable_snippets/connecting_listeners',
        'docs/reusable_snippets/build_and_train_classifier',
      ],
      link: {
        type: 'generated-index',
        description: 'Common patterns for quick use',
      },
    },
    {
      type: 'category',
      label: 'Data integrations',
      collapsed: false,
      link: {
        type: 'doc',
        id: 'docs/data_integrations/intro',
      },
      items: [
        'docs/data_integrations/mongodb',
        {
          type: 'category',
          label: 'SQL Databases',
          collapsed: false,
          link: {
            type: 'doc',
            id: 'docs/data_integrations/sql',
          },
          items: [
            'docs/data_integrations/mysql',
            'docs/data_integrations/postgresql',
            'docs/data_integrations/snowflake',
            'docs/data_integrations/sqlite',
            'docs/data_integrations/duckdb',
          ]
        },
        'docs/data_integrations/pandas', 
      ]
    },
    {
      type: 'category',
      label: 'AI integrations',
      collapsed: false,
      link:{
        type: 'generated-index',
        title: 'AI Integrations',
        description:
          "Learn more about our AI Integrations which consists of AI models, AI APIs and Frameworks",
      },
      items: [
        'docs/ai_integrations/anthropic',
        'docs/ai_integrations/cohere',
        'docs/ai_integrations/custom',
        'docs/ai_integrations/jina',
        'docs/ai_integrations/llama_cpp',
        'docs/ai_integrations/openai',
        'docs/ai_integrations/pytorch',
        'docs/ai_integrations/sentence_transformers',
        'docs/ai_integrations/sklearn',
        'docs/ai_integrations/transformers',
      ]
      
    },
    {
      type: 'category',
      label: 'Fundamentals',
      link: {
        type: 'doc',
        id: 'docs/fundamentals/overview',
      },
      items: [
        'docs/fundamentals/class_hierarchy',
        'docs/fundamentals/design',
        'docs/fundamentals/component_abstraction',
        'docs/fundamentals/datalayer_overview',
        'docs/fundamentals/data_transmision',
        'docs/fundamentals/vector_search_algorithm',
      ]
    },
    {
      type: 'category',
      label: 'Production features',
      link: {
        type: 'doc',
        id: 'docs/production/overview',
      },
      items: [
        'docs/production/development_vs_cluster_mode',
        'docs/production/command_line_interface',
        'docs/production/change_data_capture',
        'docs/production/yaml_formalism',
        'docs/production/rest_api',
        'docs/production/non_blocking_ray_jobs',
        'docs/production/vector_comparison_service',
      ],
    },
    {
      type: 'category',
      label: 'Use cases',
      collapsed: true,
      collapsible: true,
      items: [{ type: 'autogenerated', dirName: 'use_cases' }],
      link: {
        type: 'generated-index',
        description:
          'Common and useful use-cases implemented in SuperDuperDB with a walkthrough',
      },
    },

    {
      type: 'category',
      label: 'Reference',
      items: [
        {
          type: 'link',
          label: 'API Reference', // The link label
          href: 'https://docs.superduperdb.com/apidocs/source/superduperdb.html', // The external URL
        },
        {
          type: 'link',
          label: 'Change log', // The link label
          href: 'https://raw.githubusercontent.com/SuperDuperDB/superduperdb/main/CHANGELOG.md', // The external URL
        },
      ],
    },
  ],
};

module.exports = sidebars;
